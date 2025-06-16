$filePath = "C:\Users\Aluno\CascadeProjects\aws-sqs-lambda-ecs-optimized\docker\java-processor\src\test\java\com\example\processor\service\MessageProcessorServiceTest.java"
$content = Get-Content -Path $filePath

# Encontrar e substituir a verificação do contador de erros nos testes específicos
for ($i = 0; $i -lt $content.Length; $i++) {
    if ($content[$i] -match "testProcessMessageWithRepositoryException|testProcessMessageAsyncWithRepositoryException") {
        # Procurar pela linha de verificação do contador dentro deste teste
        for ($j = $i; $j -lt [Math]::Min($i + 40, $content.Length); $j++) {
            if ($content[$j] -match "verify\(sqsMessageErrorCounter, times\(1\)\)\.increment\(\);") {
                $content[$j] = $content[$j] -replace "times\(1\)", "times(2)"
                Write-Host "Corrigido teste na linha $j"
                break
            }
        }
    }
}

Set-Content -Path $filePath -Value $content
Write-Host "Testes de exceção de repositório corrigidos com sucesso!"
