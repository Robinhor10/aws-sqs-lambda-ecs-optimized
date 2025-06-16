#!/usr/bin/env python3
"""
Produtor de mensagens para SQS que simula alto volume de tráfego.
Gera mensagens de insert (80%) e delete (20%) para simular o cenário real.
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

def generate_customer_data(customer_id=None):
    """Gera dados aleatórios de cliente para mensagens de insert."""
    if customer_id is None:
        customer_id = str(uuid.uuid4())
    
    return {
        "customerId": customer_id,
        "recordId": str(uuid.uuid4()),
        "name": fake.name(),
        "email": fake.email(),
        "address": {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "zipCode": fake.zipcode()
        },
        "phoneNumber": fake.phone_number(),
        "registrationDate": datetime.now().isoformat(),
        "lastUpdated": datetime.now().isoformat(),
        "preferences": {
            "category": random.choice(["electronics", "clothing", "books", "home", "sports"]),
            "communicationChannel": random.choice(["email", "sms", "push", "mail"]),
            "frequency": random.choice(["daily", "weekly", "monthly", "quarterly"])
        },
        "status": random.choice(["active", "inactive", "pending"]),
        # Adicionar dados aleatórios para aumentar o tamanho da mensagem
        "metadata": {
            "deviceInfo": {
                "type": random.choice(["mobile", "desktop", "tablet"]),
                "os": random.choice(["iOS", "Android", "Windows", "macOS", "Linux"]),
                "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"])
            },
            "sessionData": {
                "lastLogin": datetime.now().isoformat(),
                "ipAddress": fake.ipv4(),
                "userAgent": fake.user_agent()
            },
            "analytics": {
                "visitCount": random.randint(1, 100),
                "timeOnSite": random.randint(60, 3600),
                "referrer": fake.uri()
            }
        }
    }

def generate_delete_message(customer_id, record_id):
    """Gera uma mensagem de delete para um cliente específico."""
    return {
        "operation": "DELETE",
        "customerId": customer_id,
        "recordId": record_id,
        "timestamp": datetime.now().isoformat()
    }

def generate_insert_message(customer_data):
    """Gera uma mensagem de insert com dados do cliente."""
    return {
        "operation": "INSERT",
        "data": customer_data,
        "timestamp": datetime.now().isoformat()
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
    
    # Manter registro de clientes para gerar operações de delete
    customers = []
    total_sent = 0
    
    logger.info(f"Iniciando produtor de mensagens. Tamanho do lote: {MESSAGE_BATCH_SIZE}, Intervalo: {MESSAGE_INTERVAL_MS}ms")
    
    try:
        while True:
            batch = []
            
            for _ in range(MESSAGE_BATCH_SIZE):
                # Determinar se é insert (80%) ou delete (20%)
                is_insert = random.random() < 0.8
                
                if is_insert or len(customers) < 100:  # Sempre inserir se não tiver clientes suficientes
                    # Gerar dados de cliente para insert
                    customer_data = generate_customer_data()
                    customers.append((customer_data["customerId"], customer_data["recordId"]))
                    batch.append(generate_insert_message(customer_data))
                else:
                    # Selecionar um cliente aleatório para delete
                    if customers:
                        customer_index = random.randint(0, len(customers) - 1)
                        customer_id, record_id = customers.pop(customer_index)
                        batch.append(generate_delete_message(customer_id, record_id))
            
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
