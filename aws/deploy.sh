#!/bin/bash

#####################################################################################
# Cosmic Watch - AWS Deployment Script
# This script automates the entire AWS infrastructure setup and deployment
# 
# Usage: bash aws/deploy.sh [--environment production|staging|development]
#####################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
AWS_REGION=${AWS_REGION:-us-east-1}
STACK_NAME="${ENVIRONMENT}-cosmic-watch-stack"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install it from https://aws.amazon.com/cli/"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install it from https://www.docker.com/"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run: aws configure"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

get_aws_account_id() {
    aws sts get-caller-identity --query Account --output text
}

create_secrets() {
    log_info "Creating AWS Secrets Manager secrets..."
    
    read -sp "Enter RDS password (min 12 chars): " DB_PASSWORD
    echo
    
    read -sp "Enter JWT secret key (min 32 chars): " JWT_SECRET
    echo
    
    read -p "Enter your domain name (or press Enter for ALB DNS): " DOMAIN_NAME
    
    # Create secrets
    log_info "Storing secrets in AWS Secrets Manager..."
    
    aws secretsmanager create-secret \
        --name cosmic-watch/db-password \
        --secret-string "$DB_PASSWORD" \
        --region "$AWS_REGION" \
        2>/dev/null || aws secretsmanager update-secret \
        --secret-id cosmic-watch/db-password \
        --secret-string "$DB_PASSWORD" \
        --region "$AWS_REGION"
    
    aws secretsmanager create-secret \
        --name cosmic-watch/jwt-secret \
        --secret-string "{\"jwt_secret_key\":\"$JWT_SECRET\"}" \
        --region "$AWS_REGION" \
        2>/dev/null || aws secretsmanager update-secret \
        --secret-id cosmic-watch/jwt-secret \
        --secret-string "{\"jwt_secret_key\":\"$JWT_SECRET\"}" \
        --region "$AWS_REGION"
    
    log_success "Secrets stored successfully"
    
    echo "$DB_PASSWORD"
}

build_docker_images() {
    log_info "Building Docker images..."
    
    local ACCOUNT_ID=$(get_aws_account_id)
    local ECR_REGISTRY="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Create ECR repositories
    log_info "Creating ECR repositories..."
    
    aws ecr create-repository \
        --repository-name cosmic-watch/backend \
        --region "$AWS_REGION" \
        2>/dev/null || true
    
    aws ecr create-repository \
        --repository-name cosmic-watch/frontend \
        --region "$AWS_REGION" \
        2>/dev/null || true
    
    # Login to ECR
    log_info "Logging in to AWS ECR..."
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$ECR_REGISTRY"
    
    # Build backend
    log_info "Building backend Docker image..."
    cd "$PROJECT_DIR/backend"
    docker build -t "$ECR_REGISTRY/cosmic-watch/backend:latest" .
    
    # Build frontend
    log_info "Building frontend Docker image..."
    cd "$PROJECT_DIR/frontend"
    docker build -t "$ECR_REGISTRY/cosmic-watch/frontend:latest" .
    
    # Push images
    log_info "Pushing images to ECR..."
    docker push "$ECR_REGISTRY/cosmic-watch/backend:latest"
    docker push "$ECR_REGISTRY/cosmic-watch/frontend:latest"
    
    log_success "Docker images built and pushed successfully"
}

deploy_cloudformation() {
    log_info "Deploying CloudFormation stack..."
    
    local DB_PASSWORD=$1
    local JWT_SECRET=$2
    
    aws cloudformation deploy \
        --template-file "$PROJECT_DIR/aws/cloudformation-template.yaml" \
        --stack-name "$STACK_NAME" \
        --parameter-overrides \
            EnvironmentName="$ENVIRONMENT" \
            DBPassword="$DB_PASSWORD" \
            JWTSecretKey="$JWT_SECRET" \
        --capabilities CAPABILITY_NAMED_IAM \
        --region "$AWS_REGION" \
        --no-fail-on-empty-changeset
    
    log_success "CloudFormation stack deployed successfully"
}

get_stack_outputs() {
    log_info "Retrieving stack outputs..."
    
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs' \
        --output table
}

run_migrations() {
    log_info "Running database migrations..."
    
    local CLUSTER="${ENVIRONMENT}-cosmic-watch-cluster"
    local TASK_FAMILY="${ENVIRONMENT}-cosmic-watch-backend"
    
    # Get latest task definition
    local TASK_DEF=$(aws ecs list-task-definitions \
        --family-prefix "$TASK_FAMILY" \
        --region "$AWS_REGION" \
        --query 'taskDefinitionArns[0]' \
        --output text)
    
    if [ -z "$TASK_DEF" ] || [ "$TASK_DEF" = "None" ]; then
        log_warning "Task definition not found. Skipping migrations."
        return
    fi
    
    log_info "Executing migration task..."
    
    # Get subnet and security group from ECS service
    local SUBNET=$(aws ec2 describe-subnets \
        --filters "Name=tag:Name,Values=${ENVIRONMENT}-private-1a" \
        --region "$AWS_REGION" \
        --query 'Subnets[0].SubnetId' \
        --output text)
    
    local SG=$(aws ec2 describe-security-groups \
        --filters "Name=tag:Name,Values=${ENVIRONMENT}-ecs-sg" \
        --region "$AWS_REGION" \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
    
    if [ -z "$SUBNET" ] || [ "$SUBNET" = "None" ] || [ -z "$SG" ] || [ "$SG" = "None" ]; then
        log_warning "Could not find subnet or security group. Skipping migrations."
        return
    fi
    
    aws ecs run-task \
        --cluster "$CLUSTER" \
        --task-definition "$TASK_DEF" \
        --region "$AWS_REGION" \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET],securityGroups=[$SG]}" \
        --overrides "containerOverrides=[{name=backend,command=[alembic,upgrade,head]}]"
    
    log_success "Database migrations completed"
}

deployment_summary() {
    log_info "Retrieving deployment summary..."
    
    local ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    echo
    echo "======================== DEPLOYMENT SUMMARY ========================"
    echo "Environment: $ENVIRONMENT"
    echo "CloudFormation Stack: $STACK_NAME"
    echo "AWS Region: $AWS_REGION"
    echo ""
    echo "Application URL: http://$ALB_DNS"
    echo ""
    echo "Next Steps:"
    echo "1. Point your domain to: $ALB_DNS"
    echo "2. Setup SSL/TLS certificate using AWS Certificate Manager"
    echo "3. Update ALB listener to use HTTPS"
    echo ""
    echo "For detailed information, run:"
    echo "  aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION"
    echo ""
    echo "To view logs:"
    echo "  aws logs tail /ecs/${ENVIRONMENT}-cosmic-watch-backend --follow"
    echo "  aws logs tail /ecs/${ENVIRONMENT}-cosmic-watch-frontend --follow"
    echo "====================================================================="
    echo
}

main() {
    echo
    echo "╔═════════════════════════════════════════════════════════╗"
    echo "║   Cosmic Watch - AWS Deployment Script                  ║"
    echo "║   Environment: $ENVIRONMENT"
    echo "║   Region: $AWS_REGION"
    echo "╚═════════════════════════════════════════════════════════╝"
    echo
    
    check_prerequisites
    
    log_info "Starting deployment process..."
    
    # Create secrets and get credentials
    DB_PASSWORD=$(create_secrets)
    read -sp "Re-enter JWT secret key: " JWT_SECRET
    echo
    
    # Build and push Docker images
    build_docker_images
    
    # Deploy infrastructure
    deploy_cloudformation "$DB_PASSWORD" "$JWT_SECRET"
    
    # Display outputs
    echo
    log_success "CloudFormation outputs:"
    get_stack_outputs
    
    # Run migrations
    sleep 30  # Wait for RDS to be fully available
    run_migrations
    
    # Final summary
    deployment_summary
    
    log_success "🎉 Deployment completed successfully!"
}

# Run main function
main "$@"
