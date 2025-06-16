output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "lambda_sg_id" {
  description = "ID of the security group for Lambda functions"
  value       = aws_security_group.lambda_sg.id
}

output "ecs_sg_id" {
  description = "ID of the security group for ECS tasks"
  value       = aws_security_group.ecs_sg.id
}
