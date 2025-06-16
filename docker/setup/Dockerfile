FROM python:3.9-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar scripts de configuração
COPY setup.py .

# Executar script de configuração quando o container iniciar
CMD ["python", "setup.py"]
