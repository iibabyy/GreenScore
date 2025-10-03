FROM python:3.11-slim

WORKDIR /app

# Install system deps (pour FAISS, PyPDF etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Installer requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pas de COPY . . ici → le code sera monté par docker-compose

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]