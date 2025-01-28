#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for database to become available..."
wait-for-it ${DB_HOST}:${DB_PORT} --timeout=30 --strict

echo "Database is ready. Running migrations..."
alembic upgrade head

echo "Starting FastAPI server"
exec "$@"
