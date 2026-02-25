# Miss You App - AWS Infrastructure Summary

## Overview

Complete AWS infrastructure with Terraform for the Miss You App Flask backend with PostgreSQL database, AI message generation, and Firebase push notifications.

## Architecture Diagram

View the complete architecture in the Canvas tab or at:
```
.infracodebase/aws-architecture.json
```

## Infrastructure Components

### Networking Layer
- **VPC**: 10.0.0.0/16 with DNS support
- **Subnets**: 6 subnets across 2 availability zones
  - 2 Public subnets (10.0.0.0/24, 10.0.1.0/24) - ALB, NAT Gateways
  - 2 Private App subnets (10.0.10.0/24, 10.0.11.0/24) - ECS Fargate
  - 2 Private DB subnets (10.0.20.0/24, 10.0.21.0/24) - RDS
- **Internet Gateway**: Public internet access for ALB
- **NAT Gateways**: 2x NAT (one per AZ) for outbound app traffic
- **Route Tables**: Separate routing for public, private app, private DB

### Compute Layer
- **ECS Cluster**: Fargate-based serverless containers
- **ECS Service**: 2-10 tasks with auto-scaling
- **Task Definition**:
  - 0.5 vCPU (512 CPU units)
  - 1 GB memory
  - Port 8000 exposed
  - Gunicorn WSGI server
- **Auto Scaling**:
  - CPU target: 70%
  - Memory target: 80%
  - Scale out: 60s cooldown
  - Scale in: 300s cooldown

### Database Layer
- **RDS PostgreSQL**: Version 15.4
  - Instance: db.t3.micro (free tier eligible)
  - Storage: 20GB (auto-scale to 100GB)
  - Multi-AZ: Enabled in production
  - Encryption: At rest with AES256
  - Backups: 7-day retention
  - Performance Insights: Enabled

### Load Balancing
- **Application Load Balancer**:
  - HTTP listener on port 80
  - HTTPS listener on port 443 (when domain configured)
  - Health checks: /health endpoint every 30s
  - Cross-zone load balancing enabled

### Container Registry
- **ECR Repository**:
  - Image scanning on push
  - Lifecycle policy: Keep last 10 images
  - Encryption: AES256

### Security & Secrets
- **Secrets Manager**:
  - Database credentials (username, password, DATABASE_URL)
  - Google Gemini API key
  - Firebase service account JSON
- **Security Groups**:
  - ALB: 80, 443 from internet
  - ECS: 8000 from ALB only
  - RDS: 5432 from ECS only

### Monitoring & Logging
- **CloudWatch Logs**:
  - ECS application logs: /ecs/miss-you-app
  - RDS database logs: /aws/rds/instance/.../postgresql
  - 7-day retention
- **CloudWatch Alarms**:
  - ECS CPU > 80%
  - RDS CPU > 80%
  - RDS storage < 2GB

### DNS & SSL (Optional)
- **Route53**: A record pointing to ALB
- **ACM Certificate**: Auto-provisioned and validated
- **HTTPS**: Automatic redirect from HTTP

## Application Configuration

### Environment Variables
All environment variables are injected via AWS Secrets Manager:

| Variable | Source | Required |
|----------|--------|----------|
| DATABASE_URL | Secrets Manager (db_credentials) | Yes |
| GOOGLE_API_KEY | Secrets Manager (google_api_key) | Optional |
| FIREBASE_SERVICE_ACCOUNT_KEY | Secrets Manager (firebase_key) | Optional |
| PORT | ECS environment | Yes (8000) |
| DEBUG | ECS environment | Yes (false) |

### Database Schema
Automatically initialized on first run:
- `users` table (id, username)
- `notifications` table (id, source_id, target_id, title, description, is_read, created_at)
- `user_devices` table (id, user_id, device_token, platform, created_at)
- Indexes on foreign keys and search columns

## Deployment Files

### Terraform Configuration
```
terraform/
├── main.tf                  # Provider and backend
├── variables.tf             # Input variables
├── outputs.tf               # Output values
├── vpc.tf                   # VPC, subnets, NAT, IGW
├── security_groups.tf       # Security group rules
├── alb.tf                   # Load balancer
├── route53.tf               # DNS and SSL
├── rds.tf                   # PostgreSQL database
├── ecs.tf                   # ECS cluster and service
├── ecr.tf                   # Container registry
├── secrets.tf               # Secrets Manager
├── cloudwatch.tf            # Logs and alarms
├── .gitignore               # Ignore sensitive files
├── terraform.tfvars.example # Configuration template
├── deploy.sh                # Automated deployment
├── README.md                # Detailed documentation
└── ALIGNMENT_CHECKLIST.md   # Verification document
```

### Documentation
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
- [terraform/README.md](./terraform/README.md) - Terraform documentation
- [terraform/ALIGNMENT_CHECKLIST.md](./terraform/ALIGNMENT_CHECKLIST.md) - Infrastructure alignment verification

## Quick Deployment

### Prerequisites
- AWS CLI configured
- Terraform >= 1.0 installed
- Docker installed

### Steps

1. **Configure variables**:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your credentials
   ```

2. **Deploy**:
   ```bash
   ./deploy.sh
   ```

3. **Access**:
   ```bash
   terraform output alb_url
   curl $(terraform output -raw alb_url)/health
   ```

## Cost Estimate

### Production Environment
| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| ECS Fargate | 2 tasks × 0.5 vCPU × 1GB | $30 |
| RDS PostgreSQL | db.t3.micro Multi-AZ | $20 |
| NAT Gateways | 2 gateways | $65 |
| ALB | 1 load balancer | $20 |
| Other | Data transfer, logs | $1 |
| **Total** | | **~$136/month** |

### Development Environment
| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| ECS Fargate | 1 task × 0.25 vCPU × 0.5GB | $7 |
| RDS PostgreSQL | db.t3.micro Single-AZ | $12 |
| NAT Gateway | 1 gateway | $32 |
| Other | | $1 |
| **Total** | | **~$50/month** |

## Architecture Highlights

### High Availability
- Multi-AZ deployment across 2 availability zones
- RDS Multi-AZ with automatic failover
- ALB distributes traffic across AZs
- Auto-scaling maintains service availability

### Security
- Private subnets for application and database
- No public internet access to app or database
- Secrets stored in AWS Secrets Manager
- RDS encryption at rest
- Security groups with least privilege
- HTTPS with ACM certificate (optional)

### Scalability
- Auto-scaling based on CPU/memory metrics
- 2-10 ECS tasks (configurable)
- RDS storage auto-scaling up to 100GB
- Fargate serverless - no server management

### Monitoring
- CloudWatch logs for application and database
- CloudWatch alarms for CPU and storage
- Performance Insights for RDS
- ALB access logs available

### Cost Optimization
- Free tier eligible components (db.t3.micro, t3.micro instances)
- NAT Gateway consolidation option
- Auto-scaling reduces idle resources
- Lifecycle policies for ECR images

## Validation Status

✅ **Terraform validated**: All configurations pass `terraform validate`
✅ **Formatting checked**: All files formatted with `terraform fmt`
✅ **Alignment verified**: 100% alignment with application codebase
✅ **Ready to deploy**: No changes needed

## Support & Troubleshooting

### Common Issues

**ECS tasks not starting**:
- Check CloudWatch logs: `aws logs tail /ecs/miss-you-app --follow`
- Verify secrets exist: `aws secretsmanager list-secrets`

**Database connection failed**:
- Verify RDS is running: `aws rds describe-db-instances`
- Check security groups allow ECS → RDS traffic

**ALB health checks failing**:
- Verify /health endpoint returns HTTP 200
- Check ECS task logs for startup errors

### Monitoring

**View logs**:
```bash
aws logs tail /ecs/miss-you-app --follow
```

**Check service status**:
```bash
aws ecs describe-services \
  --cluster miss-you-app-cluster \
  --services miss-you-app-service
```

**Get RDS endpoint**:
```bash
terraform output rds_endpoint
```

## Next Steps After Deployment

1. **Set up CI/CD**: Configure GitHub Actions or AWS CodePipeline
2. **Add monitoring**: CloudWatch dashboards and SNS notifications
3. **Configure backups**: Automated RDS snapshots
4. **Enable WAF**: Add AWS WAF for web application protection
5. **Custom domain**: Configure Route53 and ACM for HTTPS

## License

Same license as the main application.
