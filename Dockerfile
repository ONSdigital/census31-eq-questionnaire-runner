# syntax=docker/dockerfile:1

ARG RUNTIME_BASE_IMAGE_TAG=nonroot

# ---- Builder stage ----
# Installs all build tools, Python dependencies, and compiled assets.
# None of these build-time tools are present in the final image.
FROM python:3.13-slim-trixie AS builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential=12.12 \
        curl=8.14.1-2+deb13u4 \
        unzip=6.0-29+deb13u1 \
        jq=1.7.1-6+deb13u3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /runner

# Copy lockfiles first so dependency layers are cached independently of source changes
COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir "poetry==2.4.1" && \
    poetry config virtualenvs.in-project true && \
    poetry install --only main --no-root

# Copy the rest of the source and build static assets / translations
COPY . .
RUN make build

# Strip cache and unused locales from virtualenv (pycache, .pyc files, unused babel locales)
RUN find /runner/.venv/lib/python3.13/site-packages -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
    find /runner/.venv/lib/python3.13/site-packages -name "*.pyc" -delete; \
    find /runner/.venv/lib/python3.13/site-packages/babel/locale-data -name "*.dat" \
        ! -name "root.dat" \
        ! -name "en.dat" ! -name "en_*.dat" \
        ! -name "cy.dat" ! -name "cy_*.dat" \
        ! -name "ga.dat" ! -name "ga_*.dat" \
        ! -name "eo.dat" ! -name "eo_*.dat" \
        -delete 2>/dev/null; \
    true

# ---- Runtime stage ----
FROM gcr.io/distroless/python3-debian13:${RUNTIME_BASE_IMAGE_TAG}

# Copy only the virtualenv's site-packages into distroless Python's site-packages
COPY --from=builder /runner/.venv/lib/python3.13/site-packages /usr/local/lib/python3.13/dist-packages

WORKDIR /runner

# Copy only the files required to run the application
COPY --from=builder /runner/application.py ./application.py
COPY --from=builder /runner/gunicorn_config.py ./gunicorn_config.py
COPY --from=builder /runner/app ./app
COPY --from=builder /runner/templates ./templates
COPY --from=builder /runner/schemas ./schemas
COPY --from=builder /runner/eq_questionnaire_runner ./eq_questionnaire_runner

ENV WEB_SERVER_TYPE=gunicorn-async
ENV WEB_SERVER_WORKERS=3
ENV WEB_SERVER_THREADS=10
ENV WEB_SERVER_UWSGI_ASYNC_CORES=10
ENV HTTP_KEEP_ALIVE=2

EXPOSE 5000

# Distroless nonroot user
USER 65532:65532

# run_app.sh cannot be used here (no shell in distroless); gunicorn-async is
# the default WEB_SERVER_TYPE and is invoked directly via Python -m.
ENTRYPOINT ["/usr/bin/python3", "-m", "gunicorn", "application:application", \
    "--worker-class", "gevent", "--timeout", "0", \
    "-c", "gunicorn_config.py"]
