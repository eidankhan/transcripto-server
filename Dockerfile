FROM python:3.11-slim

WORKDIR /app

# Install dependencies for PostgreSQL client and build tools if needed
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev python3-dev postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app + import script + optional dump
COPY ./app ./app
COPY ./import_db.sh /app/import_db.sh
RUN chmod +x /app/import_db.sh

# If you have a db_dump on the host it will be mounted by docker-compose;
# we optionally copy a snapshot into the image if present at build-time.
# COPY ./db_dump.sql /app/db_dump.sql

EXPOSE 8000

ENTRYPOINT ["/app/import_db.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
