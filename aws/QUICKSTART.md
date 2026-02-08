# AWS Deployment Quick Start Guide

## 🚀 Quick Setup (15 minutes)

### Step 1: Prerequisites
```powershell
# Windows - Install required tools
choco install awscli
choco install docker-desktop
choco install git

# macOS/Linux
brew install awscli
brew install docker
```

### Step 2: Configure AWS
```powershell
aws configure
# Enter:
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region: us-east-1
# Default output format: json
```

### Step 3: Clone Repository
```powershell
git clone https://github.com/yourusername/cosmic-watch.git
cd cosmic-watch
```

### Step 4: Deploy (Choose One)

**Option A: PowerShell (Windows)**
```powershell
cd aws
.\deploy.ps1 -Environment production -AWSRegion us-east-1
```

**Option B: Bash (Linux/macOS)**
```bash
cd aws
chmod +x deploy.sh
./deploy.sh production
```

**Option C: Manual CloudFormation Deployment**
```bash
aws cloudformation deploy \
  --template-file aws/cloudformation-template.yaml \
  --stack-name production-cosmic-watch-stack \
  --parameter-overrides \
    EnvironmentName=production \
    DBPassword=YourSecurePassword123! \
    JWTSecretKey=YourJWTSecret32CharactersOrMore \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Step 5: Wait for Deployment
The deployment takes 10-15 minutes. Check status:
```bash
# Check CloudFormation stack
aws cloudformation describe-stacks \
  --stack-name production-cosmic-watch-stack \
  --region us-east-1

# Check ECS services
aws ecs describe-services \
  --cluster production-cosmic-watch-cluster \
  --services production-cosmic-watch-backend production-cosmic-watch-frontend \
  --region us-east-1
```

### Step 6: Get Application URL
```bash
aws cloudformation describe-stacks \
  --stack-name production-cosmic-watch-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text
```

---

## 🔧 Configuration Files

### Backend Environment Variables
Create or update in AWS ECS Task Definition:
```env
DATABASE_URL=postgresql://cosmicwatch:PASSWORD@[RDS-ENDPOINT]:5432/cosmic_watch_db
REDIS_URL=redis://[REDIS-ENDPOINT]:6379
JWT_SECRET_KEY=[YOUR_JWT_SECRET]
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["https://yourdomain.com"]
ENVIRONMENT=production
```

### Frontend Environment Variables
Built into Docker image at build time:
```env
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_APP_NAME=Cosmic Watch
VITE_APP_VERSION=1.0.0
```

---

## 📊 Architecture Components

| Component | Service | Cost/Month |
|-----------|---------|-----------|
| **Load Balancer** | ALB | ~$16 |
| **Backend Container** | ECS Fargate (2x) | ~$25 |
| **Frontend Container** | ECS Fargate (2x) | ~$25 |
| **Database** | RDS PostgreSQL | ~$15 |
| **Cache** | ElastiCache Redis | ~$12 |
| **Total** | | ~$93 |

---

## 🔐 Security Best Practices

### 1. Secrets Management
```bash
# Store all secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name cosmic-watch/db-password \
  --secret-string "YOUR_PASSWORD" \
  --region us-east-1

# Reference in ECS task definition as SecureString
```

### 2. SSL/TLS Certificate
```bash
# Request certificate from ACM
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names www.yourdomain.com \
  --region us-east-1

# Validate via email, then update ALB listener
```

### 3. VPC Security
- Backend in private subnets (no public IP)
- Only ALB accessible from internet
- RDS and Redis in private subnets
- Security groups restrict traffic by port

### 4. IAM Roles
- ECS task execution role with minimal permissions
- No hardcoded credentials in containers
- Use temporary credentials via IAM roles

---

## 🚀 Deploying Code Updates

### Via GitHub Actions (Recommended)
```yaml
# Configure required secrets in GitHub:
# - AWS_ACCOUNT_ID
# - AWS_ROLE_ARN (OIDC role)

# Push to main branch triggers auto-deployment
git push origin main
```

### Manual Deployment
```bash
# Build and push images
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com

docker build -t [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/backend:latest backend/
docker push [ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/backend:latest

# Update ECS service
aws ecs update-service \
  --cluster production-cosmic-watch-cluster \
  --service production-cosmic-watch-backend \
  --force-new-deployment
```

---

## 📝 Common Tasks

### View Application Logs
```bash
# Backend logs
aws logs tail /ecs/production-cosmic-watch-backend --follow

# Frontend logs
aws logs tail /ecs/production-cosmic-watch-frontend --follow
```

### Execute Commands in Container
```bash
# Run migrations
aws ecs execute-command \
  --cluster production-cosmic-watch-cluster \
  --service production-cosmic-watch-backend \
  --container backend \
  --interactive \
  --command "alembic upgrade head"
```

### Scale Services
```bash
# Set desired count
aws ecs update-service \
  --cluster production-cosmic-watch-cluster \
  --service production-cosmic-watch-backend \
  --desired-count 5 \
  --region us-east-1
```

### Database Backup
```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier production-cosmic-watch-db \
  --db-snapshot-identifier backup-$(date +%s) \
  --region us-east-1
```

---

## ⚠️ Troubleshooting

### Tasks Won't Start
```bash
# Check task logs
aws logs tail /ecs/production-cosmic-watch-backend --follow

# Describe task to see error
aws ecs describe-tasks \
  --cluster production-cosmic-watch-cluster \
  --tasks [TASK_ARN]

# Common issues:
# 1. Insufficient memory - increase task memory
# 2. Database connection error - check security groups
# 3. Image not found - verify ECR login
```

### Database Connection Issues
```bash
# Test RDS connectivity from EC2
psql -h [RDS-ENDPOINT] -U cosmicwatch -d cosmic_watch_db

# Check security group rules
aws ec2 describe-security-groups --group-ids [SG-ID]
```

### ALB Health Checks Failing
```bash
# Check target group health
aws elbv2 describe-target-health \
  --target-group-arn [TG-ARN]

# Verify backend is responding
curl http://[ALB-DNS]/health
```

---

## 🧹 Cleanup / Delete Deployment

**⚠️ Warning: This will delete all resources**

```bash
# Delete CloudFormation stack (requires database to be unprotected)
aws cloudformation delete-stack \
  --stack-name production-cosmic-watch-stack \
  --region us-east-1

# Wait for deletion to complete
aws cloudformation wait stack-delete-complete \
  --stack-name production-cosmic-watch-stack \
  --region us-east-1
```

---

## 📚 Additional Resources

- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [ECS Fargate Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-best-practices.html)
- [RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)

---

## 💬 Support

For issues or questions:
1. Check CloudWatch logs
2. Review CloudFormation events for stack errors
3. Check AWS documentation
4. Contact AWS Support (depending on plan)

**Happy Deploying! 🚀**
