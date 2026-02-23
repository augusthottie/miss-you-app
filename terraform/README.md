# Miss You App - AWS Infrastructure with Terraform

This directory contains Terraform configuration to deploy the Miss You App on AWS using a production-ready, highly available architecture.

## Architecture Overview

The infrastructure includes:

- **VPC** with public and private subnets across 2 availability zones
- **Application Load Balancer** for distributing traffic
- **ECS Fargate** for running containerized Flask application
- **RDS PostgreSQL** for database (Multi-AZ in production)
- **ECR** for Docker image registry
- **Secrets Manager** for secure credential storage
- **CloudWatch** for logs and monitoring
- **Auto Scaling** for ECS tasks based on CPU/memory
- **NAT Gateways** for outbound internet access from private subnets
- **Route53 & ACM** (optional) for custom domain with HTTPS

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Terraform** >= 1.0 installed
4. **Docker** for building application images
5. **Google Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
6. **Firebase Service Account Key** from Firebase Console

## Quick Start

### 1. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set:
- `db_password` - Strong database password
- `google_api_key` - Your Google Gemini API key
- `firebase_service_account_key` - Your Firebase service account JSON

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review the Plan

```bash
terraform plan
```

### 4. Deploy Infrastructure

```bash
terraform apply
```

Type `yes` when prompted. This will take 10-15 minutes to create all resources.

### 5. Build and Push Docker Image

After Terraform completes, use the ECR repository URL from outputs:

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url | cut -d'/' -f1)

# Build image from project root
cd ..
docker build -t miss-you-app .

# Tag and push
docker tag miss-you-app:latest $(cd terraform && terraform output -raw ecr_repository_url):latest
docker push $(cd terraform && terraform output -raw ecr_repository_url):latest
```

### 6. Access Your Application

```bash
# Get ALB URL
terraform output alb_url

# Test health endpoint
curl $(terraform output -raw alb_url)/health
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region | `us-east-1` |
| `environment` | Environment name | `prod` |
| `vpc_cidr` | VPC CIDR block | `10.0.0.0/16` |
| `db_instance_class` | RDS instance type | `db.t3.micro` |
| `app_count` | Number of ECS tasks | `2` |
| `fargate_cpu` | vCPU units (256-4096) | `512` |
| `fargate_memory` | Memory in MB | `1024` |

### Cost Optimization

For development/testing environments:

```hcl
# terraform.tfvars
environment = "dev"
db_instance_class = "db.t3.micro"
app_count = 1
fargate_cpu = "256"
fargate_memory = "512"
```

This disables Multi-AZ RDS and reduces ECS resources.

## Terraform Files Structure

```
terraform/
├── main.tf              # Provider and backend configuration
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── vpc.tf               # VPC, subnets, NAT gateways, route tables
├── security_groups.tf   # Security groups for ALB, ECS, RDS
├── alb.tf               # Application Load Balancer and target groups
├── route53.tf           # DNS and SSL certificate (optional)
├── rds.tf               # PostgreSQL database
├── ecs.tf               # ECS cluster, service, task definitions
├── ecr.tf               # Container registry
├── secrets.tf           # Secrets Manager for credentials
├── cloudwatch.tf        # Logs and monitoring
└── README.md            # This file
```

## Database Initialization

The application automatically initializes the database schema on first run. Check ECS logs:

```bash
aws logs tail /ecs/miss-you-app --follow
```

## Updating the Application

After pushing a new Docker image:

```bash
aws ecs update-service \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --service $(terraform output -raw ecs_service_name) \
  --force-new-deployment
```

## Custom Domain Setup (Optional)

### 1. Prerequisites

- Registered domain with Route53 hosted zone
- Update `terraform.tfvars`:

```hcl
domain_name = "api.example.com"
create_route53_record = true
```

### 2. Apply Changes

```bash
terraform apply
```

Terraform will:
1. Request ACM certificate
2. Create DNS validation records
3. Wait for certificate validation
4. Configure ALB with HTTPS listener
5. Create Route53 A record

### 3. Access via HTTPS

```bash
curl https://api.example.com/health
```

## Monitoring and Logs

### View Application Logs

```bash
aws logs tail /ecs/miss-you-app --follow
```

### CloudWatch Metrics

- ECS CPU/Memory utilization
- RDS performance metrics
- ALB request count and latency

### CloudWatch Alarms

Configured alarms:
- ECS CPU > 80%
- RDS CPU > 80%
- RDS free storage < 2GB

## Troubleshooting

### ECS Tasks Not Starting

1. Check ECS service events:
```bash
aws ecs describe-services \
  --cluster $(terraform output -raw ecs_cluster_name) \
  --services $(terraform output -raw ecs_service_name)
```

2. View task logs in CloudWatch

### Database Connection Issues

Verify secrets are properly configured:
```bash
aws secretsmanager get-secret-value \
  --secret-id miss-you-app-db-credentials
```

### ALB Health Checks Failing

- Ensure `/health` endpoint returns HTTP 200
- Check security group rules allow ALB → ECS traffic
- Verify ECS tasks are running in private subnets

## Security Best Practices

✅ **Implemented:**
- Database in private subnets (no internet access)
- Application in private subnets (NAT gateway for outbound)
- Secrets stored in AWS Secrets Manager
- RDS encryption at rest
- Multi-AZ RDS for high availability (prod)
- Security groups with least privilege
- HTTPS with ACM certificate (when domain configured)

🔒 **Additional Recommendations:**
- Enable AWS WAF on ALB for production
- Implement VPC Flow Logs
- Enable AWS GuardDuty
- Set up AWS Config for compliance
- Use AWS Systems Manager Session Manager for secure access

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

⚠️ **Warning:** This will permanently delete all resources including the database. Make sure to backup data first.

## Cost Estimate

Approximate monthly costs (us-east-1):

| Service | Configuration | Cost |
|---------|---------------|------|
| ECS Fargate | 2 tasks (0.5 vCPU, 1GB) | ~$30 |
| RDS PostgreSQL | db.t3.micro, 20GB | ~$20 |
| NAT Gateway | 2 gateways | ~$65 |
| ALB | 1 load balancer | ~$20 |
| Data Transfer | ~10GB/month | ~$1 |
| **Total** | | **~$136/month** |

Cost reduction strategies:
- Use 1 NAT Gateway instead of 2 (-$32)
- Use db.t3.micro with no Multi-AZ (-$20 in dev)
- Reduce ECS task count to 1 in dev (-$15)

## Support

For issues or questions:
- Check CloudWatch logs
- Review AWS service health dashboard
- Consult [Terraform AWS Provider docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## License

Same license as the main application.
