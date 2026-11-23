FROM python:3.11-slim

# No .pyc files and unbuffered logs (so they show up immediately with `docker logs`)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////app/data/app.db

# Creates the app folder inside the container
WORKDIR /app

# Copy the dependencies in first: this way Docker reuses this layer if only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy in the rest of the files (except the ones in .dockerignore)
COPY . .

# Unprivileged user and folder for the DB (mounted as a volume)
RUN useradd --create-home appuser \
    && mkdir -p /app/data \
    && chown -R appuser /app/data
USER appuser

VOLUME ["/app/data"]
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
