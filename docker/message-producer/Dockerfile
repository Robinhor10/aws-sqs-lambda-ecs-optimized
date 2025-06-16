FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do produtor de mensagens
COPY java-processor-producer.py .
COPY producer.py .

# Executar o produtor de mensagens quando o container iniciar
CMD ["python", "java-processor-producer.py"]
