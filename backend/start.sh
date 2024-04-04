#!/bin/bash



# Perform database migrations with alembic
alembic upgrade head

# Choose the command below depending on your environment:
# For local development with hot reload:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Uncomment for production:
# gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b :8000 app.main:app
