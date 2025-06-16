# AWS SQS Lambda ECS Optimized Architecture

Este projeto implementa uma arquitetura AWS otimizada para processamento de mensagens com simulação local completa usando Docker Compose. A arquitetura inclui:

- **SQS**: Fila de mensagens para processamento assíncrono
- **Lambda Consumer**: Consumidor de mensagens SQS em lote
- **Java Processor**: Serviço Spring Boot simulando uma tarefa ECS
- **DynamoDB**: Armazenamento de dados persistente
- **Prometheus & Grafana**: Monitoramento e visualização de métricas

## Arquitetura

```
                 ┌─────────────┐
                 │   Message   │
                 │  Producer   │
                 └──────┬──────┘
                        │
                        ▼
┌─────────────┐   ┌──────────┐   ┌─────────────┐
│    Dead     │◄──┤    SQS   │◄──┤   Lambda    │
│ Letter Queue│   │   Queue  │   │  Consumer   │
└─────────────┘   └──────────┘   └──────┬──────┘
                                        │
                                        │ HTTP
                                        ▼
                                 ┌─────────────┐
                                 │    Java     │
                                 │  Processor  │
                                 └──────┬──────┘
                                        │
                                        ▼
                                 ┌─────────────┐
                                 │  DynamoDB   │
                                 │   Tables    │
                                 └─────────────┘
```

## Estrutura do Projeto

```
aws-sqs-lambda-ecs-optimized/
├── docker/
│   ├── java-processor/         # Serviço Spring Boot (ECS)
│   ├── lambda-consumer/        # Consumidor Lambda em Python
│   ├── message-producer/       # Produtor de mensagens para SQS
│   ├── monitoring/             # Configurações Prometheus/Grafana
│   └── setup/                  # Scripts para configuração inicial
├── docker-compose.yml          # Definição dos serviços
├── start-local-environment.bat # Script para iniciar ambiente
└── test-integration.py         # Script para testar integração
```

## Pré-requisitos

- Docker e Docker Compose
- Python 3.9+ (para execução dos scripts de teste)
- Java 11+ e Maven (para desenvolvimento do processador Java)

## Como Executar

1. Clone o repositório
2. Execute o script de inicialização:

```bash
./start-local-environment.bat  # Windows
# ou
bash start-local-environment.sh  # Linux/Mac
```

3. Aguarde todos os serviços iniciarem (pode levar alguns minutos)
4. Acesse os serviços:
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Java Processor: http://localhost:8080

## Testando a Integração

Execute o script de teste para verificar se todos os componentes estão funcionando corretamente:

```bash
python test-integration.py
```

## Componentes

### Message Producer

Gera mensagens simuladas para a fila SQS com operações de INSERT (80%) e DELETE (20%).

### Lambda Consumer

Consome mensagens da fila SQS em lote e envia para o Java Processor via HTTP.
Implementa otimizações como:
- Processamento em lote (10 mensagens por vez)
- Tratamento de erros com DLQ
- Timeout adequado para processamento em lote

### Java Processor

Serviço Spring Boot que simula uma tarefa ECS, processando mensagens e armazenando no DynamoDB.
Características:
- Endpoints síncronos e assíncronos
- Métricas expostas via Prometheus
- Tratamento de erros e logging detalhado
- TTL para expiração automática de dados

### Monitoramento

- **Prometheus**: Coleta métricas do Java Processor e LocalStack
- **Grafana**: Visualização de dashboards com métricas de performance

## Otimizações Implementadas

1. **Processamento em Lote**: Redução de chamadas à API e melhor throughput
2. **Configuração de Timeout**: Adequado para processamento em lote
3. **Tratamento de Erros**: DLQ para mensagens com falha
4. **TTL no DynamoDB**: Expiração automática de dados
5. **Métricas Detalhadas**: Monitoramento em tempo real
6. **Processamento Assíncrono**: Maior throughput no Java Processor

## Próximos Passos

1. Implementar testes unitários adicionais
2. Configurar CI/CD para deploy no ECS real
3. Implementar alarmes baseados em métricas
4. Otimizar configurações de escalabilidade
