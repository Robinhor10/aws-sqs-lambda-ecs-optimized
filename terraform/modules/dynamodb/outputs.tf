output "table_id" {
  description = "The ID of the DynamoDB table"
  value       = aws_dynamodb_table.main.id
}

output "table_arn" {
  description = "The ARN of the DynamoDB table"
  value       = aws_dynamodb_table.main.arn
}

output "table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.main.name
}

output "table_hash_key" {
  description = "The hash key of the DynamoDB table"
  value       = aws_dynamodb_table.main.hash_key
}

output "table_range_key" {
  description = "The range key of the DynamoDB table"
  value       = aws_dynamodb_table.main.range_key
}
