#!/bin/sh

sleep 5

source env/bin/activate

echo "API is ready, listening on : http://localhost:8000"

exec uvicorn app:app
