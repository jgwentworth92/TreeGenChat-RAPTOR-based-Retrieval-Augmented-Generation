#!/bin/bash
alembic upgrade head
exec python3 app/main.py