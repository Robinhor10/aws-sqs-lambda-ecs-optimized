variable "queue_name_prefix" {
  description = "Prefix for the SQS queue name"
  type        = string
  default     = "message-processor"
}

variable "visibility_timeout_seconds" {
  description = "The visibility timeout for the queue in seconds"
  type        = number
  default     = 180 # 3 minutes, should be at least as long as the Lambda timeout
}

variable "message_retention_seconds" {
  description = "The number of seconds Amazon SQS retains a message"
  type        = number
  default     = 86400 # 24 hours (optimized from default 4 days)
}

variable "max_message_size" {
  description = "The maximum size of messages in bytes"
  type        = number
  default     = 262144 # 256 KB (maximum allowed)
}

variable "enable_dlq" {
  description = "Whether to create a dead letter queue"
  type        = bool
  default     = true
}

variable "max_receive_count" {
  description = "The maximum number of times a message can be received before being sent to the DLQ"
  type        = number
  default     = 5
}

variable "dlq_message_retention_seconds" {
  description = "The number of seconds Amazon SQS retains a message in the DLQ"
  type        = number
  default     = 1209600 # 14 days (longer than main queue for investigation)
}

variable "queue_depth_threshold" {
  description = "The threshold for the queue depth alarm"
  type        = number
  default     = 1000
}

variable "dlq_threshold" {
  description = "The threshold for the DLQ messages alarm"
  type        = number
  default     = 1
}

variable "alarm_actions" {
  description = "Actions to execute when the alarm transitions to the ALARM state"
  type        = list(string)
  default     = []
}

variable "ok_actions" {
  description = "Actions to execute when the alarm transitions to the OK state"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
