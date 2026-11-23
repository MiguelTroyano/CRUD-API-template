FROM python:3.11-slim

# No .pyc files and unbuffered logs (shown immediately by `docker logs`)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////app/data/app.db

WORKDIR /app

# Install dependencies first so this layer stays cached when only the code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as an unprivileged user; the database lives in a mounted volume
RUN useradd --create-home appuser \
    && mkdir -p /app/data \
    && chown -R appuser /app/data
USER appuser

VOLUME ["/app/data"]
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
