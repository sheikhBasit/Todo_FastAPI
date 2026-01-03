#!/bin/bash
# Wait for DB to be ready
echo "Waiting for postgres..."

echo "Running migrations..."
alembic upgrade head

echo "Starting Hypercorn (HTTP/2 enabled)..."
hypercorn app.main:app --bind 0.0.0.0:8000 --reload