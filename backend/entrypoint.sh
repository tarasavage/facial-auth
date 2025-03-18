#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e


echo "Database is ready. Running migrations..."
alembic upgrade head

echo "Starting FastAPI server"
exec "$@"
