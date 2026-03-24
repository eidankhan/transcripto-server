FROM python:3.11-slim

WORKDIR /app

# Only install essential build tools for python deps
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

EXPOSE 8000

# Start uvicorn directly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]