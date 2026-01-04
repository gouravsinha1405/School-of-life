#!/bin/bash
set -e

wait_for_db() {
python - <<'PY'
import os
import sys
import time

import psycopg

database_url = os.environ.get("DATABASE_URL")
if not database_url:
	print("DATABASE_URL is not set", file=sys.stderr)
	sys.exit(1)

max_attempts = int(os.environ.get("DB_WAIT_MAX_ATTEMPTS", "60"))
sleep_s = float(os.environ.get("DB_WAIT_SLEEP_SECONDS", "2"))

for attempt in range(1, max_attempts + 1):
	try:
		with psycopg.connect(database_url, connect_timeout=5) as conn:
			with conn.cursor() as cur:
				cur.execute("SELECT 1")
				cur.fetchone()
		print("Database is ready")
		sys.exit(0)
	except Exception as exc:  # noqa: BLE001
		print(f"Waiting for database ({attempt}/{max_attempts}): {exc}")
		time.sleep(sleep_s)

print("Database did not become ready in time", file=sys.stderr)
sys.exit(1)
PY
}

echo "Waiting for database to be ready..."
wait_for_db

echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed successfully!"

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
