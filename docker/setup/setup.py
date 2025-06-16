#!/usr/bin/env python3
"""
Script para configurar os recursos AWS na LocalStack:
- Cria filas SQS (principal e DLQ)
- Cria tabela DynamoDB
- Configura permissões e políticas
"""
import os
import time
import boto3
import json
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações AWS
AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL', 'http://localstack:4566')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'test')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'test')

# Nomes dos recursos
MAIN_QUEUE_NAME = 'message-processor-main'
DLQ_NAME = 'message-processor-dlq'
DYNAMODB_TABLE = 'customer-data'
MESSAGE_PROCESSOR_TABLE = 'message-processor-data'

def wait_for_localstack():
    """Aguarda até que o LocalStack esteja pronto para receber conexões."""
    logger.info("Aguardando LocalStack iniciar...")
    
    # Cria um cliente SQS para verificar se o LocalStack está pronto
    sqs = boto3.client(
        'sqs',
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    max_retries = 30
    retries = 0
    
    while retries < max_retries:
        try:
            # Tenta listar as filas para verificar se o LocalStack está pronto
            sqs.list_queues()
            logger.info("LocalStack está pronto!")
            return True
        except Exception as e:
            logger.info(f"LocalStack ainda não está pronto. Tentativa {retries+1}/{max_retries}")
            retries += 1
            time.sleep(2)
    
    logger.error("Timeout aguardando o LocalStack iniciar")
    return False

def create_sqs_queues():
    """Cria as filas SQS (principal e DLQ) com configurações otimizadas."""
    logger.info("Criando filas SQS...")
    
    sqs = boto3.client(
        'sqs',
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    # Criar a fila DLQ primeiro
    dlq_response = sqs.create_queue(
        QueueName=DLQ_NAME,
        Attributes={
            'MessageRetentionPeriod': '1209600',  # 14 dias para investigação
            'VisibilityTimeout': '180',  # 3 minutos
        }
    )
    dlq_url = dlq_response['QueueUrl']
    
    # Obter o ARN da DLQ
    dlq_attrs = sqs.get_queue_attributes(
        QueueUrl=dlq_url,
        AttributeNames=['QueueArn']
    )
    dlq_arn = dlq_attrs['Attributes']['QueueArn']
    
    # Criar a fila principal com redrive policy apontando para a DLQ
    redrive_policy = {
        'deadLetterTargetArn': dlq_arn,
        'maxReceiveCount': '5'  # Após 5 tentativas, enviar para DLQ
    }
    
    main_queue_response = sqs.create_queue(
        QueueName=MAIN_QUEUE_NAME,
        Attributes={
            'MessageRetentionPeriod': '86400',  # 24 horas (otimizado)
            'VisibilityTimeout': '180',  # 3 minutos
            'RedrivePolicy': json.dumps(redrive_policy)
        }
    )
    main_queue_url = main_queue_response['QueueUrl']
    
    logger.info(f"Fila principal criada: {main_queue_url}")
    logger.info(f"Fila DLQ criada: {dlq_url}")
    
    return main_queue_url, dlq_url

def create_dynamodb_tables():
    """Cria as tabelas DynamoDB para armazenar os dados dos clientes e mensagens processadas."""
    logger.info("Criando tabelas DynamoDB...")
    
    dynamodb = boto3.client(
        'dynamodb',
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    # Criar tabela para dados de clientes
    customer_table = dynamodb.create_table(
        TableName=DYNAMODB_TABLE,
        KeySchema=[
            {
                'AttributeName': 'customerId',
                'KeyType': 'HASH'  # Chave de partição
            },
            {
                'AttributeName': 'recordId',
                'KeyType': 'RANGE'  # Chave de classificação
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'customerId',
                'AttributeType': 'S'  # String
            },
            {
                'AttributeName': 'recordId',
                'AttributeType': 'S'  # String
            }
        ],
        BillingMode='PAY_PER_REQUEST'  # Modo sob demanda para otimização de custos
    )
    
    logger.info(f"Tabela DynamoDB criada: {DYNAMODB_TABLE}")
    
    # Criar tabela para o processador Java
    message_table = dynamodb.create_table(
        TableName=MESSAGE_PROCESSOR_TABLE,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Chave de partição
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Chave de classificação
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'  # String
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'  # String
            }
        ],
        BillingMode='PAY_PER_REQUEST',  # Modo sob demanda para otimização de custos
        TimeToLiveSpecification={
            'Enabled': True,
            'AttributeName': 'expiryTime'
        }
    )
    
    logger.info(f"Tabela DynamoDB para processador Java criada: {MESSAGE_PROCESSOR_TABLE}")
    
    return customer_table, message_table

def main():
    """Função principal que configura todos os recursos necessários."""
    if not wait_for_localstack():
        return
    
    try:
        main_queue_url, dlq_url = create_sqs_queues()
        customer_table, message_table = create_dynamodb_tables()
        
        logger.info("Configuração concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro durante a configuração: {str(e)}")

if __name__ == "__main__":
    main()
