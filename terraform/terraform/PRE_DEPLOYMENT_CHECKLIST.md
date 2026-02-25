# Pre-Deployment Checklist

Use this checklist before deploying the Miss You App infrastructure to AWS.

## ☑️ Prerequisites

### Tools Installed
- [ ] **Terraform** >= 1.0
  ```bash
  terraform version
  ```
- [ ] **AWS CLI** v2
  ```bash
  aws --version
  ```
- [ ] **Docker**
  ```bash
  docker --version
  ```

### AWS Configuration
- [ ] **AWS credentials configured**
  ```bash
  aws sts get-caller-identity
  # Should return your AWS account ID
  ```
- [ ] **Correct AWS region selected** (default: us-east-1)
  ```bash
  aws configure get region
  ```
- [ ] **Sufficient IAM permissions** (Admin or permissions for VPC, ECS, RDS, etc.)

---

## ☑️ Required Secrets & API Keys

### Google Gemini API Key
- [ ] **Obtained from Google AI Studio**
  - URL: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
  - Format: String (e.g., "AIzaSy...")
- [ ] **Tested and working**

### Firebase Service Account Key
- [ ] **Downloaded from Firebase Console**
  - Go to Project Settings → Service Accounts
  - Click "Generate new private key"
  - Format: JSON object
- [ ] **Valid JSON format verified**
  ```bash
  cat serviceAccountKey.json | jq .
  # Should display formatted JSON without errors
  ```

### Database Password
- [ ] **Strong password generated** (min 16 characters, mix of chars)
  ```bash
  # Generate secure password
  openssl rand -base64 24
  ```
- [ ] **Password saved in secure location** (password manager)

---

## ☑️ Configuration Files

### terraform.tfvars
- [ ] **Created from example**
  ```bash
  cp terraform.tfvars.example terraform.tfvars
  ```
- [ ] **Edited with actual values**
  - [ ] `db_password` - Changed from default
  - [ ] `google_api_key` - Real API key
  - [ ] `firebase_service_account_key` - Complete JSON
- [ ] **Sensitive file ignored by git**
  ```bash
  git status
  # terraform.tfvars should NOT appear
  ```

### Variables Review
Review these configurable settings:

- [ ] **aws_region** - Default: us-east-1 (change if needed)
- [ ] **environment** - "prod" or "dev"
- [ ] **db_instance_class** - db.t3.micro (free tier) or larger
- [ ] **app_count** - 2 for prod, 1 for dev
- [ ] **fargate_cpu** - 512 (0.5 vCPU) or adjust
- [ ] **fargate_memory** - 1024 (1GB) or adjust

---

## ☑️ Cost Considerations

### Estimated Monthly Costs
- [ ] **Understood cost implications**
  - Production: ~$136/month
  - Development: ~$50/month
- [ ] **Budget alerts configured** (optional)
  - Set up in AWS Billing console
- [ ] **Free tier awareness**
  - Some services are free tier eligible
  - Check your account's free tier status

### Cost Optimization Options
- [ ] **Consider development settings** for testing
  - Single NAT Gateway (-$32/month)
  - Single-AZ RDS (-$10/month)
  - Fewer ECS tasks (-$15/month)
  - Smaller instance sizes

---

## ☑️ Domain Configuration (Optional)

If using custom domain:

- [ ] **Domain registered** (in Route53 or external)
- [ ] **Route53 hosted zone exists**
  ```bash
  aws route53 list-hosted-zones
  ```
- [ ] **Domain name set in terraform.tfvars**
  ```hcl
  domain_name = "api.example.com"
  create_route53_record = true
  ```
- [ ] **Understood certificate validation** will take 5-10 minutes

If NOT using custom domain:
- [ ] **Domain variables left empty**
  ```hcl
  domain_name = ""
  create_route53_record = false
  ```

---

## ☑️ Pre-Deployment Validation

### Terraform Validation
- [ ] **Initialize Terraform**
  ```bash
  terraform init
  # Should succeed without errors
  ```
- [ ] **Validate configuration**
  ```bash
  terraform validate
  # Should return "Success! The configuration is valid."
  ```
- [ ] **Review plan**
  ```bash
  terraform plan
  # Review resources to be created (~45 resources)
  ```

### Expected Resources
The plan should create approximately:
- [ ] 1 VPC
- [ ] 6 Subnets (2 public, 2 private app, 2 private DB)
- [ ] 1 Internet Gateway
- [ ] 2 NAT Gateways
- [ ] Multiple Route Tables
- [ ] 3 Security Groups
- [ ] 1 Application Load Balancer
- [ ] 1 ECS Cluster + Service
- [ ] 1 RDS Database
- [ ] 1 ECR Repository
- [ ] 3 Secrets Manager secrets
- [ ] CloudWatch log groups and alarms

---

## ☑️ Application Files

### Docker Image
- [ ] **Dockerfile exists** in project root
- [ ] **requirements.txt present**
- [ ] **app.py, db.py present**
- [ ] **queries/init.sql exists**
- [ ] **All Python dependencies listed**

### Application Configuration
- [ ] **Health endpoint implemented** (/health)
- [ ] **Port 8000 configured** in app
- [ ] **Database initialization code** (init_db) present
- [ ] **Environment variables read** from process.env

---

## ☑️ Deployment Timeline

Understand the deployment timeline:

1. **Terraform Apply**: 10-15 minutes
   - VPC and networking: 2-3 min
   - RDS database: 5-8 min (Multi-AZ takes longer)
   - ECS cluster: 1-2 min
   - ALB and target groups: 2-3 min

2. **Docker Build & Push**: 2-5 minutes
   - Depends on internet speed

3. **ECS Service Start**: 2-3 minutes
   - Pull image from ECR
   - Start tasks
   - Pass health checks

**Total**: 15-25 minutes for complete deployment

---

## ☑️ Security Checklist

- [ ] **Secrets not committed to git**
  ```bash
  git status
  # Ensure no .tfvars, .env, or keys visible
  ```
- [ ] **Strong database password** (16+ chars)
- [ ] **API keys from official sources** only
- [ ] **.gitignore includes sensitive patterns**
- [ ] **Service account key not shared** publicly

---

## ☑️ Rollback Plan

Before deploying, understand the rollback process:

- [ ] **Destroy command known**
  ```bash
  terraform destroy
  ```
- [ ] **Understood data loss implications**
  - RDS database will be deleted
  - Backups configured (7-day retention)
  - Final snapshot taken (production only)
- [ ] **Manual backup option considered**
  ```bash
  # Create manual RDS snapshot before major changes
  aws rds create-db-snapshot \
    --db-instance-identifier miss-you-app-db \
    --db-snapshot-identifier manual-backup-$(date +%Y%m%d)
  ```

---

## ☑️ Post-Deployment Verification

Plan to verify after deployment:

- [ ] **Check ALB URL**
  ```bash
  terraform output alb_url
  ```
- [ ] **Test health endpoint**
  ```bash
  curl $(terraform output -raw alb_url)/health
  ```
- [ ] **View application logs**
  ```bash
  aws logs tail /ecs/miss-you-app --follow
  ```
- [ ] **Verify database connection**
  - Check logs for successful DB init
- [ ] **Test API endpoints**
  - Register user
  - Send notification
  - Check notifications

---

## ☑️ Documentation Access

Know where to find help:

- [ ] **Deployment guide**: [../DEPLOYMENT.md](../DEPLOYMENT.md)
- [ ] **Terraform README**: [README.md](README.md)
- [ ] **Alignment checklist**: [ALIGNMENT_CHECKLIST.md](ALIGNMENT_CHECKLIST.md)
- [ ] **Infrastructure summary**: [../INFRASTRUCTURE_SUMMARY.md](../INFRASTRUCTURE_SUMMARY.md)

---

## 🚀 Ready to Deploy

Once all boxes are checked:

```bash
cd terraform
./deploy.sh
```

The script will:
1. Verify prerequisites
2. Check AWS credentials
3. Show deployment plan
4. Create infrastructure (after confirmation)
5. Build and push Docker image (optional)
6. Update ECS service
7. Display access URLs

---

## ⚠️ Important Reminders

1. **First deployment takes 15-25 minutes** - be patient
2. **Database initialization happens automatically** on first run
3. **ALB DNS propagation** may take 2-3 minutes
4. **HTTPS setup** (with domain) adds 5-10 minutes for certificate validation
5. **Monitor CloudWatch logs** during first deployment
6. **Costs begin immediately** after resources are created
7. **Don't forget to destroy** test environments when done

---

## 📞 Need Help?

If something goes wrong:

1. Check CloudWatch logs first
2. Review Terraform output for errors
3. Verify all checklist items above
4. Consult troubleshooting section in DEPLOYMENT.md
5. Check AWS service health dashboard

---

**Last Updated**: February 2025
**Terraform Version**: >= 1.0
**AWS Provider Version**: ~> 5.0
