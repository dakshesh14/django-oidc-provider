#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

case "$1" in
  web)
    echo "Starting Django server..."
    python manage.py collectstatic --noinput
    python manage.py migrate --noinput
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
    ;;

  worker)
    echo "Starting Celery worker..."
    exec celery -A config.celery_app worker -l INFO
    ;;

  beat)
    echo "Starting Celery beat..."
    exec celery -A config.celery_app beat -l INFO
    ;;

  flower)
    echo "Waiting for Celery workers to be available..."
    until timeout 10 celery -A config.celery_app inspect ping; do
      >&2 echo "Celery workers not available"
      sleep 2
    done

    echo "Starting Flower..."
    exec celery \
      -A config.celery_app \
      -b "${REDIS_URL}" \
      flower \
      --basic_auth="${CELERY_FLOWER_USER}:${CELERY_FLOWER_PASSWORD}"
    ;;

  *)
    echo "Unknown command: $1"
    exec "$@"
    ;;
esac
