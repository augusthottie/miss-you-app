# AWS Deployment Guide

This document provides a complete guide to deploying the Miss You App on AWS using Terraform.

## Architecture

![AWS Architecture Diagram](.infracodebase/aws-architecture.json)

The application runs on a production-ready AWS infrastructure featuring:

- **High Availability**: Multi-AZ deployment with 2 availability zones
- **Auto Scaling**: ECS Fargate tasks scale based on CPU/memory utilization
- **Security**: Private subnets for app and database, Secrets Manager for credentials
- **Monitoring**: CloudWatch logs and metrics with alarms
- **Load Balancing**: Application Load Balancer with health checks

## Quick Start

### 1. Prerequisites

Install required tools:
- [Terraform](https://www.terraform.io/downloads) >= 1.0
- [AWS CLI](https://aws.amazon.com/cli/)
- [Docker](https://www.docker.com/get-started)

Configure AWS credentials:
```bash
aws configure
```

### 2. Configure Deployment

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and provide:
- `db_password` - Strong PostgreSQL password
- `google_api_key` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `firebase_service_account_key` - Download from Firebase Console

### 3. Deploy with Automated Script

```bash
cd terraform
./deploy.sh
```

The script will:
1. Validate prerequisites
2. Initialize Terraform
3. Show deployment plan
4. Create AWS resources (~15 minutes)
5. Build and push Docker image to ECR
6. Deploy application to ECS

### 4. Access Your Application

After deployment completes:

```bash
# Get application URL
terraform output alb_url

# Test health endpoint
curl $(terraform output -raw alb_url)/health

# View logs
aws logs tail /ecs/miss-you-app --follow
```

## Manual Deployment Steps

If you prefer manual control:

### Step 1: Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Step 2: Build and Push Docker Image

```bash
# Get ECR repository URL
ECR_URL=$(terraform output -raw ecr_repository_url)
REGION=$(terraform output -raw aws_region || echo "us-east-1")

# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin ${ECR_URL%%/*}

# Build and push from project root
cd ..
docker build -t miss-you-app .
docker tag miss-you-app:latest $ECR_URL:latest
docker push $ECR_URL:latest
```

### Step 3: Verify Deployment

```bash
# Check ECS service status
aws ecs describe-services \
  --cluster miss-you-app-cluster \
  --services miss-you-app-service

# View application logs
aws logs tail /ecs/miss-you-app --follow
```

## Configuration Options

### Environment Sizes

**Production** (default):
```hcl
environment = "prod"
db_instance_class = "db.t3.micro"
app_count = 2
fargate_cpu = "512"
fargate_memory = "1024"
```

**Development** (cost-optimized):
```hcl
environment = "dev"
db_instance_class = "db.t3.micro"
app_count = 1
fargate_cpu = "256"
fargate_memory = "512"
```

### Custom Domain with HTTPS

If you have a domain in Route53:

```hcl
domain_name = "api.example.com"
create_route53_record = true
```

This automatically:
- Requests ACM SSL certificate
- Creates DNS validation records
- Configures HTTPS on ALB
- Redirects HTTP to HTTPS

## Application Updates

### Deploy New Version

```bash
# Push new image
cd terraform
./deploy.sh --push-image

# Or manually
docker build -t miss-you-app .
docker tag miss-you-app:latest $(terraform output -raw ecr_repository_url):latest
docker push $(terraform output -raw ecr_repository_url):latest

# Force ECS to pull new image
aws ecs update-service \
  --cluster miss-you-app-cluster \
  --service miss-you-app-service \
  --force-new-deployment
```

### Update Infrastructure

```bash
cd terraform
terraform plan
terraform apply
```

## Monitoring

### CloudWatch Dashboards

View metrics in AWS Console:
- ECS cluster utilization
- RDS performance metrics
- ALB request counts and latency
- Application logs

### Configured Alarms

- ECS CPU utilization > 80%
- RDS CPU utilization > 80%
- RDS free storage < 2GB

### View Logs

```bash
# Application logs
aws logs tail /ecs/miss-you-app --follow

# RDS logs
aws logs tail /aws/rds/instance/miss-you-app-db/postgresql --follow
```

## Troubleshooting

### ECS Tasks Failing

```bash
# Check service events
aws ecs describe-services \
  --cluster miss-you-app-cluster \
  --services miss-you-app-service \
  --query 'services[0].events[0:5]'

# Check task logs
aws logs tail /ecs/miss-you-app --follow
```

### Database Connection Issues

```bash
# Verify RDS is running
aws rds describe-db-instances \
  --db-instance-identifier miss-you-app-db

# Check secrets
aws secretsmanager get-secret-value \
  --secret-id miss-you-app-db-credentials
```

### ALB Health Checks Failing

- Verify ECS tasks are in RUNNING state
- Check security groups allow ALB → ECS traffic on port 8000
- Ensure `/health` endpoint returns HTTP 200

## Cost Estimates

**Production Environment** (~$136/month):
- ECS Fargate: 2 tasks × 0.5 vCPU × 1GB = ~$30
- RDS PostgreSQL: db.t3.micro × Multi-AZ = ~$20
- NAT Gateways: 2 × $0.045/hour = ~$65
- ALB: 1 load balancer = ~$20
- Other (CloudWatch, data transfer) = ~$1

**Development Environment** (~$50/month):
- ECS Fargate: 1 task × 0.25 vCPU × 0.5GB = ~$7
- RDS PostgreSQL: db.t3.micro × Single-AZ = ~$12
- NAT Gateway: 1 × $0.045/hour = ~$32
- Other = ~$1

### Cost Optimization

1. **Use Fargate Spot** for non-production (up to 70% savings)
2. **Single NAT Gateway** instead of 2 (-$32/month)
3. **Stop RDS** when not in use (dev environments)
4. **Use smaller instance types** for development

## Security Checklist

✅ Implemented:
- Database in private subnets (no internet access)
- Application in private subnets with NAT gateway for outbound
- Secrets stored in AWS Secrets Manager
- RDS encryption at rest enabled
- Security groups with least privilege
- HTTPS with ACM certificate (optional)
- CloudWatch monitoring and alarms

🔒 Additional recommendations:
- Enable AWS WAF on ALB for production
- Implement VPC Flow Logs
- Enable AWS GuardDuty for threat detection
- Set up AWS Config for compliance monitoring
- Use AWS Systems Manager Session Manager for secure SSH alternative

## Cleanup

To destroy all infrastructure:

```bash
cd terraform
./deploy.sh --destroy

# Or manually
terraform destroy
```

⚠️ **Warning**: This permanently deletes all resources including the database. Backup important data first!

## Support Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- Project README: [README.md](./README.md)
- Terraform README: [terraform/README.md](./terraform/README.md)

## Next Steps

After successful deployment:

1. **Set up CI/CD**: Configure GitHub Actions or AWS CodePipeline for automated deployments
2. **Configure Monitoring**: Set up CloudWatch dashboards and SNS notifications for alarms
3. **Implement Backup Strategy**: Configure automated RDS snapshots and retention policies
4. **Enable WAF**: Add AWS WAF rules to protect against common web exploits
5. **Set up Domain**: Configure custom domain with Route53 and HTTPS

## License

Same license as the main application.
