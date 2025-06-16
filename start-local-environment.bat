@echo off
echo Iniciando ambiente local AWS otimizado...

REM Parar containers existentes
echo Parando containers existentes...
docker-compose down

REM Limpar volumes se necessário
REM echo Limpando volumes...
REM docker volume rm aws-sqs-lambda-ecs-optimized_grafana-data aws-sqs-lambda-ecs-optimized_prometheus-data aws-sqs-lambda-ecs-optimized_localstack-data

REM Iniciar todos os serviços
echo Iniciando serviços...
docker-compose up -d

echo.
echo Ambiente iniciado! Serviços disponíveis:
echo - LocalStack: http://localhost:4566
echo - Java Processor: http://localhost:8080
echo - Prometheus: http://localhost:9090
echo - Grafana: http://localhost:3000 (admin/admin)
echo.
echo Para visualizar logs: docker-compose logs -f
echo Para parar o ambiente: docker-compose down
echo.
echo Aguardando serviços inicializarem...
timeout /t 10 /nobreak > nul

echo Verificando status dos serviços...
docker-compose ps
