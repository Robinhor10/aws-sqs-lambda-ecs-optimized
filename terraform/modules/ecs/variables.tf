variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "message-processor-cluster"
}

variable "task_definition_family" {
  description = "Family name of the task definition"
  type        = string
  default     = "message-processor"
}

variable "service_name" {
  description = "Name of the ECS service"
  type        = string
  default     = "message-processor-service"
}

variable "container_name" {
  description = "Name of the container"
  type        = string
  default     = "message-processor"
}

variable "container_image" {
  description = "Docker image for the container"
  type        = string
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8080
}

variable "task_cpu" {
  description = "CPU units for the task (1 vCPU = 1024 CPU units)"
  type        = number
  default     = 512
}

variable "task_memory" {
  description = "Memory for the task in MiB"
  type        = number
  default     = 1024
}

variable "desired_count" {
  description = "Desired count of tasks"
  type        = number
  default     = 1
}

variable "min_capacity" {
  description = "Minimum capacity for auto scaling"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum capacity for auto scaling"
  type        = number
  default     = 10
}

variable "use_fargate_spot" {
  description = "Whether to use Fargate Spot for cost optimization"
  type        = bool
  default     = true
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the ECS tasks"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs for the ECS tasks"
  type        = list(string)
}

variable "enable_load_balancer" {
  description = "Whether to create an Application Load Balancer"
  type        = bool
  default     = false
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the ALB"
  type        = list(string)
  default     = []
}

variable "lb_security_group_ids" {
  description = "List of security group IDs for the ALB"
  type        = list(string)
  default     = []
}

variable "health_check_path" {
  description = "Path for ALB health check"
  type        = string
  default     = "/health"
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  type        = string
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "sqs_queue_resource_label" {
  description = "Resource label for SQS queue in auto scaling policy"
  type        = string
}

variable "sqs_queue_name" {
  description = "Name of the SQS queue for CloudWatch dashboard"
  type        = string
}

variable "target_messages_per_task" {
  description = "Target number of messages per task for auto scaling"
  type        = number
  default     = 100
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
