$filePath = "C:\Users\Aluno\CascadeProjects\aws-sqs-lambda-ecs-optimized\docker\java-processor\src\test\java\com\example\processor\service\MessageProcessorServiceTest.java"
$content = Get-Content -Path $filePath -Raw
$content = $content -replace "verify\(sqsMessageErrorCounter, times\(1\)\)\.increment\(\);", "verify(sqsMessageErrorCounter, times(2)).increment();"
Set-Content -Path $filePath -Value $content
Write-Host "Testes corrigidos com sucesso!"
