#!/usr/bin/env python3
"""
Consumidor Lambda que implementa as otimizações recomendadas:
1. Processamento em lote (10 mensagens por vez)
2. Memória otimizada (simulado com limites de recursos)
3. Timeout adequado para processamento em lote
4. Tratamento de erros com DLQ
"""
import os
import time
import json
import logging
import uuid
import requests
from datetime import datetime
import boto3
import threading
import queue

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações AWS
AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL', 'http://localstack:4566')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'test')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'test')

# Configurações do consumidor
SQS_QUEUE_NAME = os.environ.get('SQS_QUEUE_NAME', 'message-processor-main')
SQS_DLQ_NAME = os.environ.get('SQS_DLQ_NAME', 'message-processor-dlq')
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '10'))  # Otimizado para processar 10 mensagens por vez
ECS_SERVICE_URL = os.environ.get('ECS_SERVICE_URL', 'http://java-processor:8080/process')

# Métricas para monitoramento
metrics = {
    'messages_processed': 0,
    'batch_processed': 0,
    'errors': 0,
    'processing_time_ms': 0,
    'avg_processing_time_ms': 0
}

# Clientes AWS
sqs = boto3.client(
    'sqs',
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def wait_for_queues():
    """Aguarda até que as filas SQS estejam disponíveis."""
    logger.info(f"Aguardando filas SQS '{SQS_QUEUE_NAME}' e '{SQS_DLQ_NAME}' estarem disponíveis...")
    
    max_retries = 30
    retries = 0
    
    main_queue_url = None
    dlq_url = None
    
    while retries < max_retries:
        try:
            # Verificar fila principal
            if not main_queue_url:
                response = sqs.list_queues(QueueNamePrefix=SQS_QUEUE_NAME)
                if 'QueueUrls' in response and len(response['QueueUrls']) > 0:
                    main_queue_url = response['QueueUrls'][0]
                    logger.info(f"Fila principal encontrada: {main_queue_url}")
            
            # Verificar DLQ
            if not dlq_url:
                response = sqs.list_queues(QueueNamePrefix=SQS_DLQ_NAME)
                if 'QueueUrls' in response and len(response['QueueUrls']) > 0:
                    dlq_url = response['QueueUrls'][0]
                    logger.info(f"DLQ encontrada: {dlq_url}")
            
            # Se ambas as filas foram encontradas, retornar
            if main_queue_url and dlq_url:
                return main_queue_url, dlq_url
        except Exception as e:
            logger.info(f"Erro ao verificar filas SQS: {str(e)}. Tentativa {retries+1}/{max_retries}")
        
        retries += 1
        time.sleep(2)
    
    logger.error(f"Timeout aguardando as filas SQS")
    return main_queue_url, dlq_url

def process_message(message):
    """
    Processa uma mensagem individual, enviando para o serviço ECS.
    Retorna True se processado com sucesso, False caso contrário.
    """
    try:
        # Extrair o corpo da mensagem
        body = json.loads(message['Body'])
        
        # Enviar para o serviço ECS (Java Processor)
        response = requests.post(
            ECS_SERVICE_URL,
            json=body,
            headers={'Content-Type': 'application/json'},
            timeout=5  # Timeout para a requisição HTTP
        )
        
        # Verificar se a resposta foi bem-sucedida
        if response.status_code == 200:
            logger.info(f"Mensagem processada com sucesso: {body.get('operation', 'UNKNOWN')} - {response.json().get('status', 'OK')}")
            return True
        else:
            logger.error(f"Erro ao processar mensagem: Status {response.status_code}, Resposta: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão com o serviço ECS: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        return False

def process_message_batch(queue_url, dlq_url, batch_size):
    """
    Recebe e processa um lote de mensagens da fila SQS.
    Implementa a otimização de processamento em lote.
    """
    try:
        # Receber mensagens em lote
        start_time = time.time()
        
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=batch_size,  # Otimizado para processar 10 mensagens por vez
            VisibilityTimeout=180,  # 3 minutos (mesmo valor configurado na fila)
            WaitTimeSeconds=5  # Long polling para reduzir custos
        )
        
        messages = response.get('Messages', [])
        if not messages:
            return 0
        
        logger.info(f"Recebido lote com {len(messages)} mensagens")
        
        # Processar cada mensagem no lote
        successful_messages = []
        failed_messages = []
        
        for message in messages:
            if process_message(message):
                successful_messages.append({
                    'Id': message['MessageId'],
                    'ReceiptHandle': message['ReceiptHandle']
                })
            else:
                failed_messages.append(message)
        
        # Remover mensagens processadas com sucesso da fila
        if successful_messages:
            sqs.delete_message_batch(
                QueueUrl=queue_url,
                Entries=[{'Id': msg['Id'], 'ReceiptHandle': msg['ReceiptHandle']} for msg in successful_messages]
            )
        
        # Enviar mensagens com falha para a DLQ
        for message in failed_messages:
            try:
                # Extrair o corpo da mensagem
                body = json.loads(message['Body'])
                
                # Adicionar informações de erro
                body['error'] = {
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'Failed to process by ECS service'
                }
                
                # Enviar para a DLQ
                sqs.send_message(
                    QueueUrl=dlq_url,
                    MessageBody=json.dumps(body)
                )
                
                # Remover da fila principal
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
                
                logger.info(f"Mensagem com falha enviada para DLQ: {message['MessageId']}")
            except Exception as e:
                logger.error(f"Erro ao mover mensagem para DLQ: {str(e)}")
        
        # Atualizar métricas
        processing_time = (time.time() - start_time) * 1000  # em milissegundos
        metrics['messages_processed'] += len(successful_messages)
        metrics['batch_processed'] += 1
        metrics['errors'] += len(failed_messages)
        metrics['processing_time_ms'] += processing_time
        
        if metrics['batch_processed'] > 0:
            metrics['avg_processing_time_ms'] = metrics['processing_time_ms'] / metrics['batch_processed']
        
        logger.info(f"Processado lote em {processing_time:.2f}ms. Sucesso: {len(successful_messages)}, Falhas: {len(failed_messages)}")
        
        return len(messages)
    except Exception as e:
        logger.error(f"Erro ao processar lote de mensagens: {str(e)}")
        metrics['errors'] += 1
        return 0

def print_metrics():
    """Imprime métricas periodicamente para monitoramento."""
    while True:
        logger.info(f"MÉTRICAS: Mensagens processadas: {metrics['messages_processed']}, "
                   f"Lotes: {metrics['batch_processed']}, "
                   f"Erros: {metrics['errors']}, "
                   f"Tempo médio de processamento: {metrics['avg_processing_time_ms']:.2f}ms")
        time.sleep(10)

def main():
    """Função principal que consome mensagens da fila SQS em lote."""
    main_queue_url, dlq_url = wait_for_queues()
    if not main_queue_url or not dlq_url:
        logger.error("Não foi possível encontrar as filas SQS. Encerrando.")
        return
    
    # Iniciar thread para imprimir métricas
    metrics_thread = threading.Thread(target=print_metrics, daemon=True)
    metrics_thread.start()
    
    logger.info(f"Iniciando consumidor Lambda. Tamanho do lote: {BATCH_SIZE}")
    
    try:
        while True:
            # Processar um lote de mensagens
            messages_processed = process_message_batch(main_queue_url, dlq_url, BATCH_SIZE)
            
            # Se não houver mensagens, aguardar um pouco antes de verificar novamente
            if messages_processed == 0:
                time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Consumidor Lambda interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no consumidor Lambda: {str(e)}")

if __name__ == "__main__":
    main()
