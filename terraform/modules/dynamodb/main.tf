###################################################
# DynamoDB Module with Optimized Configuration
###################################################

# DynamoDB table with optimized settings
resource "aws_dynamodb_table" "main" {
  name         = var.table_name
  hash_key     = var.hash_key
  range_key    = var.range_key
  
  # Optimization: On-demand capacity mode for cost optimization
  billing_mode = "PAY_PER_REQUEST"
  
  # Optimization: TTL for automatic data cleanup
  ttl {
    attribute_name = var.ttl_attribute
    enabled        = true
  }
  
  # Table attributes
  attribute {
    name = var.hash_key
    type = "S"
  }
  
  attribute {
    name = var.range_key
    type = "S"
  }
  
  # Add GSI if specified
  dynamic "global_secondary_index" {
    for_each = var.global_secondary_indexes
    content {
      name               = global_secondary_index.value.name
      hash_key           = global_secondary_index.value.hash_key
      range_key          = global_secondary_index.value.range_key
      projection_type    = global_secondary_index.value.projection_type
      non_key_attributes = lookup(global_secondary_index.value, "non_key_attributes", null)
    }
  }
  
  # Optimization: Point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }
  
  # Tags for cost tracking
  tags = merge(
    var.tags,
    {
      Name = var.table_name
    }
  )
}

# CloudWatch Alarm for consumed read capacity
resource "aws_cloudwatch_metric_alarm" "read_capacity_alarm" {
  alarm_name          = "${var.table_name}-read-capacity-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ConsumedReadCapacityUnits"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = var.read_capacity_threshold
  alarm_description   = "This alarm monitors DynamoDB consumed read capacity"
  
  dimensions = {
    TableName = aws_dynamodb_table.main.name
  }
  
  alarm_actions = var.alarm_actions
  ok_actions    = var.ok_actions
  
  tags = var.tags
}

# CloudWatch Alarm for consumed write capacity
resource "aws_cloudwatch_metric_alarm" "write_capacity_alarm" {
  alarm_name          = "${var.table_name}-write-capacity-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ConsumedWriteCapacityUnits"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = var.write_capacity_threshold
  alarm_description   = "This alarm monitors DynamoDB consumed write capacity"
  
  dimensions = {
    TableName = aws_dynamodb_table.main.name
  }
  
  alarm_actions = var.alarm_actions
  ok_actions    = var.ok_actions
  
  tags = var.tags
}
