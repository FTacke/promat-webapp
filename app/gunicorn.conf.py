"""Gunicorn settings for the production container (started from app/Dockerfile)."""

import os

bind = "0.0.0.0:5000"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
worker_tmp_dir = "/dev/shm"
errorlog = "-"
accesslog = "-"
# Never log the query string or the Referer: password-reset links carry their one-time token as
# `?token=...`, and the browser sends that URL as Referer with the follow-up requests of the reset page.
# %(U)s is the path without query; %(q)s, %(r)s and %(f)s are intentionally absent.
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(m)s %(U)s %(H)s" %(s)s %(b)s "%(a)s" %(L)s'
