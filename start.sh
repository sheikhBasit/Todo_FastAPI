#!/bin/bash
# Wait for DB to be ready
echo "Waiting for postgres..."
# Run migrations
alembic upgrade head
# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000