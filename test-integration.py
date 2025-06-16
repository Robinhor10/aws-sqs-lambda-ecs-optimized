#!/usr/bin/env python3
"""
Script para testar a integração entre os componentes do sistema:
- Envia mensagens para a fila SQS
- Verifica se o Lambda Consumer está processando as mensagens
- Verifica se o Java Processor está recebendo e processando as requisições
- Verifica se os dados estão sendo armazenados no DynamoDB
"""
import os
import time
import json
import boto3
import requests
import logging
import uuid
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações AWS
AWS_ENDPOINT_URL = "http://localhost:4566"
AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "test"
AWS_SECRET_ACCESS_KEY = "test"

# Configurações do teste
SQS_QUEUE_NAME = "message-processor-main"
DYNAMODB_TABLE = "message-processor-data"
JAVA_PROCESSOR_URL = "http://localhost:8080"
TEST_MESSAGE_COUNT = 10
WAIT_TIME = 2  # segundos para aguardar entre verificações

def create_sqs_client():
    """Cria um cliente SQS para interagir com a LocalStack."""
    return boto3.client(
        'sqs',
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

def create_dynamodb_client():
    """Cria um cliente DynamoDB para interagir com a LocalStack."""
    return boto3.client(
        'dynamodb',
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

def get_queue_url(sqs_client):
    """Obtém a URL da fila SQS."""
    try:
        response = sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)
        return response['QueueUrl']
    except Exception as e:
        logger.error(f"Erro ao obter URL da fila: {str(e)}")
        return None

def send_test_messages(sqs_client, queue_url, count=10):
    """Envia mensagens de teste para a fila SQS."""
    messages = []
    
    for i in range(count):
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Alternar entre INSERT e DELETE
        operation = "INSERT" if i % 5 != 0 else "DELETE"
        
        if operation == "INSERT":
            message = {
                "id": message_id,
                "timestamp": timestamp,
                "operation": operation,
                "name": f"Test User {i}",
                "email": f"test{i}@example.com",
                "address": f"Address {i}, Test City",
                "phone": f"+1234567{i:03d}"
            }
        else:
            # Para DELETE, usamos o ID da mensagem anterior
            prev_message = messages[-1] if messages else {"id": str(uuid.uuid4()), "timestamp": datetime.now().isoformat()}
            message = {
                "id": prev_message["id"],
                "timestamp": prev_message["timestamp"],
                "operation": operation
            }
        
        messages.append(message)
        
        # Enviar mensagem para a fila
        try:
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message)
            )
            logger.info(f"Mensagem {i+1}/{count} enviada: {message['operation']} - {message['id']}")
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem {i+1}: {str(e)}")
    
    return messages

def check_java_processor_health():
    """Verifica se o Java Processor está funcionando corretamente."""
    try:
        response = requests.get(f"{JAVA_PROCESSOR_URL}/health")
        if response.status_code == 200:
            logger.info(f"Java Processor está saudável: {response.text}")
            return True
        else:
            logger.error(f"Java Processor retornou status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Erro ao verificar saúde do Java Processor: {str(e)}")
        return False

def test_direct_processor_call():
    """Testa uma chamada direta ao processador Java."""
    message_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    test_request = {
        "id": message_id,
        "timestamp": timestamp,
        "operation": "INSERT",
        "name": "Direct Test User",
        "email": "direct@example.com",
        "address": "Direct Test Address",
        "phone": "+9876543210"
    }
    
    try:
        response = requests.post(
            f"{JAVA_PROCESSOR_URL}/process", 
            json=test_request
        )
        
        if response.status_code == 200:
            logger.info(f"Chamada direta ao processador bem-sucedida: {response.json()}")
            return message_id, timestamp, True
        else:
            logger.error(f"Chamada direta ao processador falhou com status {response.status_code}: {response.text}")
            return message_id, timestamp, False
    except Exception as e:
        logger.error(f"Erro ao chamar diretamente o processador: {str(e)}")
        return message_id, timestamp, False

def check_dynamodb_record(dynamodb_client, message_id, timestamp):
    """Verifica se um registro foi criado no DynamoDB."""
    try:
        response = dynamodb_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={
                'id': {'S': message_id},
                'timestamp': {'S': timestamp}
            }
        )
        
        if 'Item' in response:
            logger.info(f"Registro encontrado no DynamoDB: {response['Item']}")
            return True
        else:
            logger.info(f"Registro não encontrado no DynamoDB para ID {message_id}")
            return False
    except Exception as e:
        logger.error(f"Erro ao verificar registro no DynamoDB: {str(e)}")
        return False

def main():
    """Função principal que executa os testes de integração."""
    logger.info("Iniciando testes de integração...")
    
    # Verificar saúde do Java Processor
    if not check_java_processor_health():
        logger.error("Java Processor não está saudável. Abortando testes.")
        return
    
    # Criar clientes AWS
    sqs_client = create_sqs_client()
    dynamodb_client = create_dynamodb_client()
    
    # Obter URL da fila
    queue_url = get_queue_url(sqs_client)
    if not queue_url:
        logger.error("Não foi possível obter a URL da fila SQS. Abortando testes.")
        return
    
    # Testar chamada direta ao processador
    message_id, timestamp, success = test_direct_processor_call()
    if not success:
        logger.error("Teste de chamada direta falhou. Verifique se o Java Processor está funcionando corretamente.")
    
    # Aguardar um pouco para garantir que o registro foi criado
    logger.info("Aguardando processamento...")
    time.sleep(WAIT_TIME)
    
    # Verificar se o registro foi criado no DynamoDB
    if not check_dynamodb_record(dynamodb_client, message_id, timestamp):
        logger.error("Registro não encontrado no DynamoDB após chamada direta. Verifique a configuração do DynamoDB.")
    
    # Enviar mensagens de teste para a fila SQS
    logger.info(f"Enviando {TEST_MESSAGE_COUNT} mensagens de teste para a fila SQS...")
    messages = send_test_messages(sqs_client, queue_url, TEST_MESSAGE_COUNT)
    
    # Aguardar processamento das mensagens
    logger.info(f"Aguardando {WAIT_TIME * 3} segundos para processamento das mensagens...")
    time.sleep(WAIT_TIME * 3)
    
    # Verificar alguns registros no DynamoDB
    success_count = 0
    for i, message in enumerate(messages):
        if message["operation"] == "INSERT":
            if check_dynamodb_record(dynamodb_client, message["id"], message["timestamp"]):
                success_count += 1
    
    logger.info(f"Verificação concluída: {success_count} de {len([m for m in messages if m['operation'] == 'INSERT'])} registros INSERT encontrados no DynamoDB")
    
    logger.info("Testes de integração concluídos!")

if __name__ == "__main__":
    main()
