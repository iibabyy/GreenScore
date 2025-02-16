#!/bin/sh

sleep 5

echo "API is ready, listening on : http://localhost:8000"

exec uvicorn app:app
