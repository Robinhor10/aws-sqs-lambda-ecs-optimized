#!/usr/bin/env python3
"""
Produtor de mensagens para SQS que simula alto volume de tráfego para o processador Java.
Gera mensagens de insert (80%) e delete (20%) no formato esperado pelo processador Java.
"""
import os
import time
import json
import random
import logging
import uuid
from datetime import datetime
import boto3
from faker import Faker

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações AWS
AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL', 'http://localstack:4566')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'test')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'test')

# Configurações do produtor
SQS_QUEUE_NAME = os.environ.get('SQS_QUEUE_NAME', 'message-processor-main')
MESSAGE_BATCH_SIZE = int(os.environ.get('MESSAGE_BATCH_SIZE', '100'))
MESSAGE_INTERVAL_MS = int(os.environ.get('MESSAGE_INTERVAL_MS', '1000'))

# Inicializar Faker para gerar dados aleatórios
fake = Faker()

# Cliente SQS
sqs = boto3.client(
    'sqs',
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def wait_for_queue():
    """Aguarda até que a fila SQS esteja disponível."""
    logger.info(f"Aguardando fila SQS '{SQS_QUEUE_NAME}' estar disponível...")
    
    max_retries = 30
    retries = 0
    
    while retries < max_retries:
        try:
            # Tenta listar as filas para verificar se a fila existe
            response = sqs.list_queues(QueueNamePrefix=SQS_QUEUE_NAME)
            if 'QueueUrls' in response and len(response['QueueUrls']) > 0:
                queue_url = response['QueueUrls'][0]
                logger.info(f"Fila SQS encontrada: {queue_url}")
                return queue_url
            else:
                logger.info(f"Fila SQS '{SQS_QUEUE_NAME}' ainda não existe. Tentativa {retries+1}/{max_retries}")
        except Exception as e:
            logger.info(f"Erro ao verificar fila SQS: {str(e)}. Tentativa {retries+1}/{max_retries}")
        
        retries += 1
        time.sleep(2)
    
    logger.error(f"Timeout aguardando a fila SQS '{SQS_QUEUE_NAME}'")
    return None

def generate_insert_message():
    """Gera uma mensagem de insert para o processador Java."""
    message_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    return {
        "id": message_id,
        "timestamp": timestamp,
        "operation": "INSERT",
        "name": fake.name(),
        "email": fake.email(),
        "address": fake.address().replace('\n', ', '),
        "phone": fake.phone_number()
    }

def generate_delete_message(message_id, timestamp):
    """Gera uma mensagem de delete para o processador Java."""
    return {
        "id": message_id,
        "timestamp": timestamp,
        "operation": "DELETE"
    }

def send_message_batch(queue_url, messages):
    """Envia um lote de mensagens para a fila SQS."""
    try:
        entries = []
        for i, message in enumerate(messages):
            entries.append({
                'Id': str(i),
                'MessageBody': json.dumps(message)
            })
        
        response = sqs.send_message_batch(
            QueueUrl=queue_url,
            Entries=entries
        )
        
        successful = len(response.get('Successful', []))
        failed = len(response.get('Failed', []))
        
        logger.info(f"Enviado lote de {successful} mensagens com sucesso, {failed} falhas")
        
        if failed > 0:
            logger.warning(f"Falhas no envio: {response.get('Failed')}")
            
        return successful, failed
    except Exception as e:
        logger.error(f"Erro ao enviar mensagens em lote: {str(e)}")
        return 0, len(messages)

def main():
    """Função principal que gera e envia mensagens para a fila SQS."""
    queue_url = wait_for_queue()
    if not queue_url:
        logger.error("Não foi possível encontrar a fila SQS. Encerrando.")
        return
    
    # Manter registro de mensagens para gerar operações de delete
    messages = []
    total_sent = 0
    
    logger.info(f"Iniciando produtor de mensagens para o processador Java. Tamanho do lote: {MESSAGE_BATCH_SIZE}, Intervalo: {MESSAGE_INTERVAL_MS}ms")
    
    try:
        while True:
            batch = []
            
            for _ in range(MESSAGE_BATCH_SIZE):
                # Determinar se é insert (80%) ou delete (20%)
                is_insert = random.random() < 0.8
                
                if is_insert or len(messages) < 100:  # Sempre inserir se não tiver mensagens suficientes
                    # Gerar dados para insert
                    message = generate_insert_message()
                    messages.append((message["id"], message["timestamp"]))
                    batch.append(message)
                else:
                    # Selecionar uma mensagem aleatória para delete
                    if messages:
                        message_index = random.randint(0, len(messages) - 1)
                        message_id, timestamp = messages.pop(message_index)
                        batch.append(generate_delete_message(message_id, timestamp))
            
            # Enviar o lote de mensagens
            successful, _ = send_message_batch(queue_url, batch)
            total_sent += successful
            
            logger.info(f"Total de mensagens enviadas: {total_sent}")
            
            # Aguardar o intervalo configurado
            time.sleep(MESSAGE_INTERVAL_MS / 1000.0)
    except KeyboardInterrupt:
        logger.info("Produtor de mensagens interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no produtor de mensagens: {str(e)}")

if __name__ == "__main__":
    main()
