# Utilizar una imagen oficial de Python 3.10 como imagen base
FROM python:3.10

# Definir el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias de sistema necesarias
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev gcc \
       # Dependencias para otras posibles librerías de Python que requieran compilación
    && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de requisitos e instalar las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto Django al directorio de trabajo
COPY . .

# Ejecutar migraciones y recopilar archivos estáticos
# Nota: Considera manejar migraciones y la recopilación de estáticos fuera de Dockerfile para entornos de producción
# RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Exponer el puerto en el que Daphne escuchará
EXPOSE 8000

# Comando para ejecutar la aplicación usando Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]
