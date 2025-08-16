#!/usr/bin/env bash
set -e
source .venv/bin/activate || true
exec uvicorn app.main:app --host ${APP_HOST:-0.0.0.0} --port ${APP_PORT:-8000}
