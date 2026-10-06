#!/bin/sh
set -e

echo "Waiting for Postgres..."
python - <<'PY'
import os, time
import psycopg2

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
name = os.environ.get("POSTGRES_DB", "legis_poc")
user = os.environ.get("POSTGRES_USER", "legis")
password = os.environ.get("POSTGRES_PASSWORD", "legis")

for i in range(60):
    try:
        psycopg2.connect(host=host, port=port, dbname=name, user=user, password=password).close()
        print("Postgres is ready.")
        break
    except Exception as exc:
        print(f"  attempt {i+1}: {exc}")
        time.sleep(1)
else:
    raise SystemExit("Postgres did not become ready in time")
PY

python manage.py migrate --noinput
python manage.py seed_legislation
python manage.py collectstatic --noinput 2>/dev/null || true

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
