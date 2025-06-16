FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do consumidor Lambda
COPY consumer.py .

# Executar o consumidor quando o container iniciar
CMD ["python", "consumer.py"]
