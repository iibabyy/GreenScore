FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN chmod +x /app/run.sh

EXPOSE 8000


# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# CMD ["sleep", "infinity"]
ENTRYPOINT ["/app/run.sh"]