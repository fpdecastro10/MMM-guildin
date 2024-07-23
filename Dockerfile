# Usar la imagen oficial de Python como base
FROM python:3.11

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requisitos en el contenedor
COPY requirements.txt requirements.txt

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el contenido de la aplicación en el contenedor
COPY . .

RUN export $(grep -v '^#' .env | xargs)

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "main.py"]
