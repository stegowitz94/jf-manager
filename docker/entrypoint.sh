#!/bin/sh
set -eu
if [ "${1:-}" = "gunicorn" ]; then
  echo "Waiting for PostgreSQL..."
  python manage.py wait_for_db
  echo "Applying committed migrations..."
  python manage.py migrate --noinput
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
fi
exec "$@"
