#!/usr/bin/env bash
# Auto-migrate, pin Site/Google for this Render host, then serve.
set -euo pipefail
cd "$(dirname "$0")/.."
python manage.py migrate --noinput
python manage.py prepare_deploy_auth || true
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120
