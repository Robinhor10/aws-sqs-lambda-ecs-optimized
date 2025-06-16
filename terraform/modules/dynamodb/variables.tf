variable "table_name" {
  description = "Name of the DynamoDB table"
  type        = string
  default     = "message-processor-data"
}

variable "hash_key" {
  description = "Hash key for the DynamoDB table"
  type        = string
  default     = "id"
}

variable "range_key" {
  description = "Range key for the DynamoDB table"
  type        = string
  default     = "timestamp"
}

variable "ttl_attribute" {
  description = "Name of the TTL attribute for automatic data cleanup"
  type        = string
  default     = "expiry_time"
}

variable "global_secondary_indexes" {
  description = "List of global secondary indexes for the DynamoDB table"
  type        = list(object({
    name               = string
    hash_key           = string
    range_key          = string
    projection_type    = string
    non_key_attributes = optional(list(string))
  }))
  default     = []
}

variable "enable_point_in_time_recovery" {
  description = "Whether to enable point-in-time recovery"
  type        = bool
  default     = true
}

variable "read_capacity_threshold" {
  description = "Threshold for the read capacity alarm"
  type        = number
  default     = 240
}

variable "write_capacity_threshold" {
  description = "Threshold for the write capacity alarm"
  type        = number
  default     = 240
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
