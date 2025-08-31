# Imagen base de Python
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la API
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando por defecto (ejecutar API)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7777"]
