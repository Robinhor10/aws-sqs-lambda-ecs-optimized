variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "message-processor"
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
