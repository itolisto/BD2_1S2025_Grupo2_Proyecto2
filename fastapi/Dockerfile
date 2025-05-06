# Usar una imagen base de Python 3.9
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos
COPY requirements.txt /app/

# Crear un entorno virtual
RUN python -m venv /venv

# Activar el entorno virtual e instalar las dependencias
RUN /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install -r requirements.txt

# Copiar todo el código de la API
COPY . /app/

# Exponer el puerto en el que correrá la API
EXPOSE 6500

# Establecer la variable de entorno para usar el entorno virtual
ENV PATH="/venv/bin:$PATH"

# Comando para iniciar la aplicación FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6500"]
