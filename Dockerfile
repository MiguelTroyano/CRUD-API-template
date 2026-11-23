FROM python:3.11-slim

# Sin .pyc y con logs sin buffer (se ven al momento con `docker logs`)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////app/data/proyecto.db

# Crea la carpeta app en el contenedor
WORKDIR /app

# Introduce primero las dependencias: así Docker reutiliza esta capa si sólo cambia el código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Luego introduce el resto de archivos (salvo los de .dockerignore)
COPY . .

# Usuario sin privilegios y carpeta para la BBDD (se monta como volumen)
RUN useradd --create-home appuser \
    && mkdir -p /app/data \
    && chown -R appuser /app/data
USER appuser

VOLUME ["/app/data"]
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
