###################################################
# SQS Module with Optimized Configuration
###################################################

# Main SQS Queue with optimized settings
resource "aws_sqs_queue" "main_queue" {
  name                       = "${var.queue_name_prefix}-main"
  visibility_timeout_seconds = var.visibility_timeout_seconds
  
  # Optimization: Reduced message retention period (24 hours instead of default 4 days)
  message_retention_seconds  = var.message_retention_seconds
  
  # Optimization: Set reasonable max message size based on expected payload
  max_message_size           = var.max_message_size
  
  # Optimization: Enable server-side encryption for security
  sqs_managed_sse_enabled    = true
  
  # Optimization: Configure DLQ redrive policy if enabled
  redrive_policy = var.enable_dlq ? jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dead_letter_queue[0].arn
    maxReceiveCount     = var.max_receive_count
  }) : null
  
  # Tags for cost tracking
  tags = merge(
    var.tags,
    {
      Name = "${var.queue_name_prefix}-main"
    }
  )
}

# Dead Letter Queue (DLQ) for failed message processing
resource "aws_sqs_queue" "dead_letter_queue" {
  count = var.enable_dlq ? 1 : 0
  
  name                       = "${var.queue_name_prefix}-dlq"
  visibility_timeout_seconds = var.visibility_timeout_seconds
  
  # DLQ should have longer retention to allow investigation
  message_retention_seconds  = var.dlq_message_retention_seconds
  
  # Optimization: Enable server-side encryption for security
  sqs_managed_sse_enabled    = true
  
  # Tags for cost tracking
  tags = merge(
    var.tags,
    {
      Name = "${var.queue_name_prefix}-dlq"
    }
  )
}

# CloudWatch Alarm for monitoring queue depth
resource "aws_cloudwatch_metric_alarm" "queue_depth_alarm" {
  alarm_name          = "${var.queue_name_prefix}-depth-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Average"
  threshold           = var.queue_depth_threshold
  alarm_description   = "This alarm monitors SQS queue depth"
  
  dimensions = {
    QueueName = aws_sqs_queue.main_queue.name
  }
  
  alarm_actions = var.alarm_actions
  ok_actions    = var.ok_actions
  
  # Tags for cost tracking
  tags = merge(
    var.tags,
    {
      Name = "${var.queue_name_prefix}-depth-alarm"
    }
  )
}

# CloudWatch Alarm for monitoring DLQ messages
resource "aws_cloudwatch_metric_alarm" "dlq_messages_alarm" {
  count = var.enable_dlq ? 1 : 0
  
  alarm_name          = "${var.queue_name_prefix}-dlq-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Sum"
  threshold           = var.dlq_threshold
  alarm_description   = "This alarm monitors SQS DLQ messages"
  
  dimensions = {
    QueueName = aws_sqs_queue.dead_letter_queue[0].name
  }
  
  alarm_actions = var.alarm_actions
  ok_actions    = var.ok_actions
  
  # Tags for cost tracking
  tags = merge(
    var.tags,
    {
      Name = "${var.queue_name_prefix}-dlq-alarm"
    }
  )
}
