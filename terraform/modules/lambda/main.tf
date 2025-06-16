###################################################
# Lambda Module with Optimized Configuration
###################################################

# IAM role for the Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name_prefix}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Lambda execution policy
resource "aws_iam_policy" "lambda_policy" {
  name        = "${var.function_name_prefix}-policy"
  description = "Policy for Lambda function to access AWS resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # CloudWatch Logs permissions
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        # SQS permissions
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:ChangeMessageVisibility"
        ]
        Effect   = "Allow"
        Resource = [
          var.sqs_arn,
          var.sqs_dlq_arn
        ]
      },
      {
        # VPC permissions
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        # ECS permissions to invoke tasks
        Action = [
          "ecs:RunTask",
          "ecs:DescribeTasks",
          "iam:PassRole"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Create Lambda function package
data "archive_file" "lambda_package" {
  type        = "zip"
  source_dir  = "${path.module}/function"
  output_path = "${path.module}/function.zip"
}

# Lambda function with optimized configuration
resource "aws_lambda_function" "processor" {
  function_name = "${var.function_name_prefix}-processor"
  description   = "Processes messages from SQS and triggers ECS tasks"
  
  filename         = data.archive_file.lambda_package.output_path
  source_code_hash = data.archive_file.lambda_package.output_base64sha256
  
  role    = aws_iam_role.lambda_role.arn
  handler = "index.handler"
  runtime = "nodejs16.x"
  
  # Optimization: Optimized memory size for cost/performance
  memory_size = var.memory_size
  
  # Optimization: Appropriate timeout for batch processing
  timeout     = var.timeout
  
  # Optimization: Reserved concurrency to control costs
  reserved_concurrent_executions = var.reserved_concurrent_executions
  
  # VPC configuration
  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }
  
  # Environment variables
  environment {
    variables = {
      ECS_CLUSTER_NAME = var.ecs_cluster_name
      ECS_TASK_DEFINITION = var.ecs_task_definition
      ECS_CONTAINER_NAME = var.ecs_container_name
      ECS_SUBNET_IDS = join(",", var.subnet_ids)
      ECS_SECURITY_GROUP_IDS = join(",", var.security_group_ids)
    }
  }
  
  # Tags for cost tracking
  tags = merge(
    var.tags,
    {
      Name = "${var.function_name_prefix}-processor"
    }
  )
}

# CloudWatch Log Group with retention policy
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${aws_lambda_function.processor.function_name}"
  retention_in_days = 14
  
  tags = var.tags
}

# SQS Event Source Mapping with batch processing
resource "aws_lambda_event_source_mapping" "sqs_event_source" {
  event_source_arn = var.sqs_arn
  function_name    = aws_lambda_function.processor.function_name
  
  # Optimization: Batch processing to reduce Lambda invocations
  batch_size       = var.batch_size
  
  # Optimization: Maximum batch window to allow batching of messages
  maximum_batching_window_in_seconds = var.maximum_batching_window_in_seconds
}

# CloudWatch Alarm for Lambda errors
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.function_name_prefix}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "This alarm monitors Lambda function errors"
  
  dimensions = {
    FunctionName = aws_lambda_function.processor.function_name
  }
  
  alarm_actions = var.alarm_actions
  ok_actions    = var.ok_actions
  
  tags = var.tags
}

# CloudWatch Alarm for Lambda throttles
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "${var.function_name_prefix}-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "This alarm monitors Lambda function throttles"
  
  dimensions = {
    FunctionName = aws_lambda_function.processor.function_name
  }
  
  alarm_actions = var.alarm_actions
  ok_actions    = var.ok_actions
  
  tags = var.tags
}

# CloudWatch Dashboard for Lambda metrics
resource "aws_cloudwatch_dashboard" "lambda_dashboard" {
  dashboard_name = "${var.function_name_prefix}-dashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.processor.function_name],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.processor.function_name],
            ["AWS/Lambda", "Throttles", "FunctionName", aws_lambda_function.processor.function_name]
          ]
          period = 300
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "Lambda Invocations, Errors, and Throttles"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.processor.function_name, {"stat": "Average"}],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.processor.function_name, {"stat": "Maximum"}]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "Lambda Duration"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", var.sqs_queue_name]
          ]
          period = 300
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "SQS Queue Depth"
        }
      }
    ]
  })
}

# Get current region
data "aws_region" "current" {}
