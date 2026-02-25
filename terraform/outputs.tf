output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "IDs of private application subnets"
  value       = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  description = "IDs of private database subnets"
  value       = aws_subnet.private_db[*].id
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  description = "URL of the Application Load Balancer"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.app.name
}

output "rds_endpoint" {
  description = "Endpoint of the RDS PostgreSQL instance"
  value       = aws_db_instance.postgresql.endpoint
}

output "rds_database_name" {
  description = "Name of the PostgreSQL database"
  value       = aws_db_instance.postgresql.db_name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for ECS tasks"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "secrets_manager_db_credentials_arn" {
  description = "ARN of the Secrets Manager secret for database credentials"
  value       = aws_secretsmanager_secret.db_credentials.arn
}

output "secrets_manager_google_api_key_arn" {
  description = "ARN of the Secrets Manager secret for Google API key"
  value       = aws_secretsmanager_secret.google_api_key.arn
}

output "secrets_manager_firebase_key_arn" {
  description = "ARN of the Secrets Manager secret for Firebase key"
  value       = aws_secretsmanager_secret.firebase_key.arn
}

output "domain_name" {
  description = "Domain name (if configured)"
  value       = var.create_route53_record && var.domain_name != "" ? var.domain_name : "Not configured"
}

output "deployment_instructions" {
  description = "Next steps for deployment"
  value       = <<-EOT

    ====================================
    DEPLOYMENT INSTRUCTIONS
    ====================================

    1. Build and push Docker image to ECR:

       aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.app.repository_url}
       docker build -t ${var.project_name} .
       docker tag ${var.project_name}:latest ${aws_ecr_repository.app.repository_url}:latest
       docker push ${aws_ecr_repository.app.repository_url}:latest

    2. Access your application:

       Application URL: http://${aws_lb.main.dns_name}
       Health Check: http://${aws_lb.main.dns_name}/health

    3. View logs:

       aws logs tail ${aws_cloudwatch_log_group.ecs.name} --follow

    4. Connect to RDS (from within VPC):

       Host: ${aws_db_instance.postgresql.address}
       Port: ${aws_db_instance.postgresql.port}
       Database: ${aws_db_instance.postgresql.db_name}
       Username: (stored in Secrets Manager)

    5. Update ECS service after pushing new image:

       aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.app.name} --force-new-deployment

    ====================================
  EOT
}
