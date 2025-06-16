output "lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = aws_lambda_function.processor.arn
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.processor.function_name
}

output "lambda_role_arn" {
  description = "The ARN of the IAM role used by Lambda function"
  value       = aws_iam_role.lambda_role.arn
}

output "lambda_log_group_name" {
  description = "The name of the CloudWatch log group for the Lambda function"
  value       = aws_cloudwatch_log_group.lambda_logs.name
}

output "lambda_event_source_mapping_id" {
  description = "The ID of the Lambda event source mapping"
  value       = aws_lambda_event_source_mapping.sqs_event_source.id
}

output "lambda_dashboard_name" {
  description = "The name of the CloudWatch dashboard for Lambda metrics"
  value       = aws_cloudwatch_dashboard.lambda_dashboard.dashboard_name
}
