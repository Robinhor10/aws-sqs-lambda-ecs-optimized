variable "function_name_prefix" {
  description = "Prefix for the Lambda function name"
  type        = string
  default     = "sqs-processor"
}

variable "memory_size" {
  description = "Amount of memory in MB for the Lambda function"
  type        = number
  default     = 1024  # Optimized for cost/performance balance
}

variable "timeout" {
  description = "Timeout in seconds for the Lambda function"
  type        = number
  default     = 30  # Optimized for batch processing
}

variable "reserved_concurrent_executions" {
  description = "Amount of reserved concurrent executions for the Lambda function"
  type        = number
  default     = 100  # Optimized to control costs
}

variable "batch_size" {
  description = "Maximum number of records to include in each batch"
  type        = number
  default     = 10  # Optimized batch size for SQS processing
}

variable "maximum_batching_window_in_seconds" {
  description = "Maximum amount of time to gather records before invoking the function"
  type        = number
  default     = 0  # No additional batching window
}

variable "sqs_arn" {
  description = "ARN of the SQS queue to trigger the Lambda function"
  type        = string
}

variable "sqs_dlq_arn" {
  description = "ARN of the SQS DLQ"
  type        = string
  default     = ""
}

variable "sqs_queue_name" {
  description = "Name of the SQS queue for CloudWatch dashboard"
  type        = string
  default     = "message-processor-main"
}

variable "vpc_id" {
  description = "ID of the VPC where the Lambda function will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the Lambda function"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs for the Lambda function"
  type        = list(string)
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster to run tasks in"
  type        = string
  default     = "message-processor-cluster"
}

variable "ecs_task_definition" {
  description = "ARN of the ECS task definition to run"
  type        = string
  default     = "message-processor:latest"
}

variable "ecs_container_name" {
  description = "Name of the container in the task definition"
  type        = string
  default     = "message-processor"
}

variable "alarm_actions" {
  description = "List of ARNs to execute when the alarm transitions to ALARM state"
  type        = list(string)
  default     = []
}

variable "ok_actions" {
  description = "List of ARNs to execute when the alarm transitions to OK state"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
