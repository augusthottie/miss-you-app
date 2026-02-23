#!/bin/bash

###############################################################################
# Miss You App - AWS Deployment Script
# This script automates the deployment process for the Miss You App on AWS
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_tools=()

    if ! command -v terraform &> /dev/null; then
        missing_tools+=("terraform")
    fi

    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
    fi

    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install the missing tools and try again."
        exit 1
    fi

    log_info "All prerequisites met!"
}

# Check if AWS credentials are configured
check_aws_credentials() {
    log_info "Checking AWS credentials..."

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured or invalid"
        log_error "Please run 'aws configure' and try again"
        exit 1
    fi

    local account_id=$(aws sts get-caller-identity --query Account --output text)
    log_info "Using AWS Account: $account_id"
}

# Check if terraform.tfvars exists
check_tfvars() {
    if [ ! -f "terraform.tfvars" ]; then
        log_error "terraform.tfvars not found!"
        log_info "Creating terraform.tfvars from example..."
        cp terraform.tfvars.example terraform.tfvars
        log_warn "Please edit terraform.tfvars with your actual values before proceeding"
        log_warn "Required values:"
        log_warn "  - db_password"
        log_warn "  - google_api_key"
        log_warn "  - firebase_service_account_key"
        exit 1
    fi
}

# Initialize Terraform
init_terraform() {
    log_info "Initializing Terraform..."
    terraform init
}

# Plan Terraform changes
plan_terraform() {
    log_info "Planning Terraform changes..."
    terraform plan -out=tfplan
}

# Apply Terraform changes
apply_terraform() {
    log_info "Applying Terraform configuration..."
    terraform apply tfplan
    rm -f tfplan
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."

    local ecr_url=$(terraform output -raw ecr_repository_url)
    local region=$(terraform output -raw aws_region || echo "us-east-1")
    local ecr_registry=$(echo "$ecr_url" | cut -d'/' -f1)

    log_info "ECR Repository: $ecr_url"

    # Login to ECR
    log_info "Logging in to ECR..."
    aws ecr get-login-password --region "$region" | docker login --username AWS --password-stdin "$ecr_registry"

    # Build image
    log_info "Building Docker image..."
    cd ..
    docker build -t miss-you-app .

    # Tag and push
    log_info "Tagging and pushing image..."
    docker tag miss-you-app:latest "$ecr_url:latest"
    docker push "$ecr_url:latest"

    cd terraform
    log_info "Docker image pushed successfully!"
}

# Force ECS service deployment
force_ecs_deployment() {
    log_info "Updating ECS service with new image..."

    local cluster=$(terraform output -raw ecs_cluster_name)
    local service=$(terraform output -raw ecs_service_name)

    aws ecs update-service \
        --cluster "$cluster" \
        --service "$service" \
        --force-new-deployment \
        --query 'service.serviceName' \
        --output text

    log_info "ECS service update initiated!"
}

# Display deployment information
show_deployment_info() {
    log_info "Deployment complete! Here's your application info:"
    echo ""
    echo "======================================"
    echo "APPLICATION INFORMATION"
    echo "======================================"
    terraform output alb_url
    echo ""
    echo "Test your application:"
    echo "  curl \$(terraform output -raw alb_url)/health"
    echo ""
    echo "View logs:"
    echo "  aws logs tail \$(terraform output -raw cloudwatch_log_group) --follow"
    echo ""
    echo "======================================"
}

# Main deployment flow
main() {
    echo ""
    log_info "Starting Miss You App deployment to AWS..."
    echo ""

    check_prerequisites
    check_aws_credentials
    check_tfvars

    # Ask for confirmation
    read -p "Do you want to proceed with deployment? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_warn "Deployment cancelled"
        exit 0
    fi

    init_terraform
    plan_terraform

    echo ""
    log_warn "Review the plan above. Press ENTER to continue or Ctrl+C to cancel..."
    read

    apply_terraform

    # Ask if user wants to build and push Docker image
    echo ""
    read -p "Do you want to build and push Docker image now? (yes/no): " build_image
    if [ "$build_image" == "yes" ]; then
        build_and_push_image
        force_ecs_deployment
    else
        log_warn "Skipping Docker image build. Remember to build and push your image later!"
        log_warn "Run: ./deploy.sh --push-image"
    fi

    echo ""
    show_deployment_info

    log_info "Deployment complete!"
}

# Handle command line arguments
case "${1:-}" in
    --push-image)
        log_info "Building and pushing Docker image only..."
        build_and_push_image
        force_ecs_deployment
        ;;
    --destroy)
        log_warn "This will DESTROY all infrastructure!"
        read -p "Are you sure? Type 'yes' to confirm: " confirm
        if [ "$confirm" == "yes" ]; then
            terraform destroy
        else
            log_warn "Destroy cancelled"
        fi
        ;;
    --help)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (no args)      - Full deployment (infrastructure + image)"
        echo "  --push-image   - Build and push Docker image only"
        echo "  --destroy      - Destroy all infrastructure"
        echo "  --help         - Show this help message"
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        log_info "Run '$0 --help' for usage information"
        exit 1
        ;;
esac
