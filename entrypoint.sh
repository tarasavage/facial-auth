#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Upgrading database"
alembic upgrade head

echo "Starting FastAPI server"
exec "$@"
