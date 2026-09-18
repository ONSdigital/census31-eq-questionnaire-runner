import os

import gunicorn

if os.getenv("WEB_SERVER_TYPE") == "gunicorn-async":
    worker_class = "gevent"
elif os.getenv("WEB_SERVER_TYPE") == "gunicorn-threads":
    worker_class = "gthread"

workers = os.getenv("WEB_SERVER_WORKERS")
threads = os.getenv("WEB_SERVER_THREADS")
keepalive = os.getenv("HTTP_KEEP_ALIVE")
timeout = 0
bind = "0.0.0.0:5000"
gunicorn.SERVER_SOFTWARE = "None"
