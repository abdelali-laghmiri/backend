#!/usr/bin/env sh
set -eu

MAX_RETRIES="${DB_STARTUP_MAX_RETRIES:-10}"
RETRY_DELAY="${DB_STARTUP_RETRY_DELAY:-3}"
ATTEMPT=1

echo "Running database migrations..."
until python -m alembic upgrade head; do
  if [ "$ATTEMPT" -ge "$MAX_RETRIES" ]; then
    echo "Alembic migrations failed after ${ATTEMPT} attempt(s)." >&2
    exit 1
  fi

  echo "Alembic migrations failed on attempt ${ATTEMPT}; retrying in ${RETRY_DELAY}s..." >&2
  ATTEMPT=$((ATTEMPT + 1))
  sleep "$RETRY_DELAY"
done

echo "Running database seeds..."
case "${RUN_SEEDS:-true}" in
  true|TRUE|1|yes|YES)
    python -m seeds.run
    ;;
  *)
    echo "Seed step skipped because RUN_SEEDS is disabled."
    ;;
esac

echo "Starting FastAPI server..."
exec python -m uvicorn main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --proxy-headers \
  --forwarded-allow-ips='*'
