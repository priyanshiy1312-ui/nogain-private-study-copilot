#!/usr/bin/env bash
cd "$(dirname "$0")/.." && set -a && [ -f .env ] && . ./.env; set +a
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
