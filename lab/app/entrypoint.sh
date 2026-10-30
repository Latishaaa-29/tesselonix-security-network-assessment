#!/bin/sh
set -eu
if [ "$#" -gt 0 ]; then exec "$@"; fi
for attempt in $(seq 1 30); do
  if flask db upgrade; then
    # One worker: in-memory rate limiting is explicitly lab-only.
    exec gunicorn --workers 1 --threads 4 --bind 0.0.0.0:5000 microblog:app
  fi
  sleep 2
done
echo 'Database migrations failed' >&2
exit 1
