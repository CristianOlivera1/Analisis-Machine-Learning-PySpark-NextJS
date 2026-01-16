# Imagen base con Python y Java
FROM python:3.11-slim-bookworm

# Instalar Java 17 (versión LTS compatible con PySpark)
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configurar JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p storage/uploads

EXPOSE 5000

ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
