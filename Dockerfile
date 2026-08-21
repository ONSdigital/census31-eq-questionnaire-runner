FROM python:3.13-slim-bookworm

EXPOSE 5000

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl=7.88.1-10+deb12u* \
        unzip=6.0-28 \
        libsnappy-dev=1.1.9-3 \
        build-essential=12.9 \
        jq=1.6-2.1+deb12u* \
    && rm -rf /var/lib/apt/lists/*

COPY . /runner
WORKDIR /runner

ENV WEB_SERVER_TYPE gunicorn-async
ENV WEB_SERVER_WORKERS 3
ENV WEB_SERVER_THREADS 10
ENV WEB_SERVER_UWSGI_ASYNC_CORES 10
ENV HTTP_KEEP_ALIVE 2
ENV GUNICORN_CMD_ARGS -c gunicorn_config.py

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN groupadd -r appuser && useradd -r -g appuser -u 9000 appuser && chown -R appuser:appuser .
RUN pip install --no-cache-dir "poetry==2.4.1" && \
    poetry config virtualenvs.create false && \
    poetry install --only main && \
    make build

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD curl -f http://localhost:5000/status || exit 1

CMD ["sh", "run_app.sh"]
