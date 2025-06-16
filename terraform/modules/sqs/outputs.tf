output "sqs_arn" {
  description = "The ARN of the SQS queue"
  value       = aws_sqs_queue.main_queue.arn
}

output "sqs_id" {
  description = "The URL of the SQS queue"
  value       = aws_sqs_queue.main_queue.id
}

output "sqs_name" {
  description = "The name of the SQS queue"
  value       = aws_sqs_queue.main_queue.name
}

output "sqs_dlq_arn" {
  description = "The ARN of the SQS DLQ"
  value       = var.enable_dlq ? aws_sqs_queue.dead_letter_queue[0].arn : null
}

output "sqs_dlq_id" {
  description = "The URL of the SQS DLQ"
  value       = var.enable_dlq ? aws_sqs_queue.dead_letter_queue[0].id : null
}

output "sqs_dlq_name" {
  description = "The name of the SQS DLQ"
  value       = var.enable_dlq ? aws_sqs_queue.dead_letter_queue[0].name : null
}
