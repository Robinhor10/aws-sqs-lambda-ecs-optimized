provider "aws" {
  region = var.aws_region
}

# Terraform state configuration
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  
  # Uncomment to use remote state
  # backend "s3" {
  #   bucket = "terraform-state-bucket-name"
  #   key    = "sqs-lambda-ecs/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# Create a VPC for our ECS cluster
module "vpc" {
  source = "./modules/vpc"
}

# SQS module with optimized configuration
module "sqs" {
  source = "./modules/sqs"
  
  # DLQ configuration
  enable_dlq = true
  
  # Retention period optimization (24 hours = 86400 seconds)
  message_retention_seconds = 86400
}

# Lambda module with optimized configuration
module "lambda" {
  source = "./modules/lambda"
  
  # Lambda configuration with optimized memory
  memory_size = 1024
  timeout     = 30
  
  # Batch processing configuration
  batch_size  = 10
  
  # Concurrency limits for cost control
  reserved_concurrent_executions = 100
  
  # SQS trigger
  sqs_arn     = module.sqs.sqs_arn
  sqs_dlq_arn = module.sqs.sqs_dlq_arn
  
  # VPC configuration
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids = [module.vpc.lambda_sg_id]
}

# ECS module
module "ecs" {
  source = "./modules/ecs"
  
  # VPC configuration
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids
  security_group_ids = [module.vpc.ecs_sg_id]
  
  # Load balancer configuration
  public_subnet_ids = module.vpc.public_subnet_ids
  
  # ECR repository for our Java application
  ecr_repository_url = module.ecr.repository_url
}

# ECR module for Docker images
module "ecr" {
  source = "./modules/ecr"
}

# DynamoDB module
module "dynamodb" {
  source = "./modules/dynamodb"
}
