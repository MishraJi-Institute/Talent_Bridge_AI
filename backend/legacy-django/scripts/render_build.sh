#!/usr/bin/env bash
# Render build: install, verify correct TalentBridge app, collectstatic.
set -euo pipefail
DJANGO="$(cd "$(dirname "$0")/.." && pwd)"
ROOT="$(cd "$DJANGO/../.." && pwd)"
cd "$DJANGO"
pip install -r requirements.txt
chmod +x scripts/render_start.sh
export DJANGO_ENV=production
export DJANGO_DEBUG=false
export DJANGO_BEHIND_PROXY=true
if [ -z "${DJANGO_SECRET_KEY:-}" ]; then
  export DJANGO_SECRET_KEY="render-build-placeholder-not-used-at-runtime"
fi
python manage.py check
python manage.py verify_production_deploy
python manage.py collectstatic --noinput