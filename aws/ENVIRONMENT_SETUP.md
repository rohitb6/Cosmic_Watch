# AWS Environment Setup Instructions

## Prerequisites

### 1. AWS Account
- Create an AWS account at https://aws.amazon.com
- Enable billing alerts for cost management
- Set up MFA (Multi-Factor Authentication) on root account

### 2. IAM User Setup

**Create a dedicated deployment user:**

```bash
# Create user
aws iam create-user --user-name cosmic-watch-deployer

# Create access key
aws iam create-access-key --user-name cosmic-watch-deployer

# Attach policies
aws iam attach-user-policy \
  --user-name cosmic-watch-deployer \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

aws iam attach-user-policy \
  --user-name cosmic-watch-deployer \
  --policy-arn arn:aws:iam::aws:policy/IAMFullAccess

# Save the access key and secret key in a secure location
```

**Minimal IAM Policy** (more restrictive):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "ec2:*",
        "ecs:*",
        "elasticloadbalancing:*",
        "rds:*",
        "elasticache:*",
        "ecr:*",
        "logs:*",
        "cloudwatch:*",
        "iam:CreateRole",
        "iam:PutRolePolicy",
        "iam:PassRole",
        "iam:GetRole",
        "iam:DeleteRole",
        "iam:DeleteRolePolicy",
        "iam:CreatePolicy",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "secretsmanager:*",
        "acm:*",
        "route53:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### 3. Configure AWS CLI

```powershell
# Windows
aws configure --profile cosmic-watch
# Enter Access Key ID
# Enter Secret Access Key  
# Default region: us-east-1
# Default output format: json

# Set as default
aws configure set default.profile cosmic-watch
```

Or set environment variables:
```powershell
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

### 4. Install Docker

**Windows:**
```powershell
# Using Chocolatey
choco install docker-desktop

# Or download from https://www.docker.com/products/docker-desktop
```

**macOS/Linux:**
```bash
# macOS
brew install --cask docker

# Linux (Ubuntu)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### 5. Setup GitHub (for CI/CD)

```bash
# Fork the repository
# Enable GitHub Actions in repository settings

# Add repository secrets (Settings → Secrets → New repository secret):
# AWS_ACCOUNT_ID: Your 12-digit AWS account ID
# AWS_ROLE_ARN: OIDC role ARN for GitHub Actions
```

**Create OIDC Role for GitHub Actions:**
```bash
# Create trust policy document
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:GITHUB_ORG/GITHUB_REPO:*"
        }
      }
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name cosmic-watch-github-actions \
  --assume-role-policy-document file://trust-policy.json

# Attach policy
aws iam attach-role-policy \
  --role-name cosmic-watch-github-actions \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# Get role ARN
aws iam get-role --role-name cosmic-watch-github-actions --query 'Role.Arn'
```

---

## Environment Variables

### Backend (.env or ECS Environment)

Create `.env` file in `backend/` directory:

```env
# Database
DATABASE_URL=postgresql://cosmicwatch:password@localhost:5432/cosmic_watch_db
DB_POOL_SIZE=10
DB_POOL_RECYCLE=3600

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","https://yourdomain.com"]

# Application
APP_NAME=Cosmic Watch
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Security
SECURITY_ALGORITHM=bcrypt
SECURITY_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_MINUTES=15
```

### Frontend (.env or Build Arguments)

Create `.env` file in `frontend/` directory:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000

# Application
VITE_APP_NAME=Cosmic Watch
VITE_APP_VERSION=1.0.0
VITE_APP_DESCRIPTION=Real-time Asteroid Monitoring & AI Chatbot

# Features
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_ERROR_TRACKING=true

# Environment
VITE_ENV=development
```

---

## AWS Secrets Manager Setup

Store sensitive data securely:

```bash
# Database password
aws secretsmanager create-secret \
  --name cosmic-watch/db-password \
  --secret-string "YourSecurePassword123!" \
  --region us-east-1

# JWT Secret
aws secretsmanager create-secret \
  --name cosmic-watch/jwt-secret \
  --secret-string '{"jwt_secret_key":"YourJWTSecretMin32Characters"}' \
  --region us-east-1

# Email configuration (optional)
aws secretsmanager create-secret \
  --name cosmic-watch/email-config \
  --secret-string '{
    "SMTP_HOST":"smtp.gmail.com",
    "SMTP_PORT":587,
    "SMTP_USER":"your-email@gmail.com",
    "SMTP_PASSWORD":"your-app-password"
  }' \
  --region us-east-1

# List secrets
aws secretsmanager list-secrets --region us-east-1

# Get secret
aws secretsmanager get-secret-value \
  --secret-id cosmic-watch/db-password \
  --region us-east-1
```

---

## AWS Account Setup Checklist

- [ ] Create AWS account
- [ ] Set up billing alerts
- [ ] Enable MFA on root account
- [ ] Create IAM user (cosmic-watch-deployer)
- [ ] Generate access keys
- [ ] Configure AWS CLI
- [ ] Install Docker
- [ ] Set up GitHub (optional, for CI/CD)
- [ ] Create OIDC role for GitHub Actions (if using GitHub)
- [ ] Create secrets in Secrets Manager
- [ ] Verify AWS CLI credentials: `aws sts get-caller-identity`
- [ ] Verify Docker: `docker --version`

---

## Verify Setup

```bash
# Check AWS CLI
aws sts get-caller-identity
# Output: Account ID, User ARN, User ID

# Check Docker
docker --version
docker run hello-world

# Check git
git --version

# Check that we can access ECR (should fail initially, that's OK)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

---

## Production Hardening

### 1. Enable CloudTrail
```bash
aws cloudtrail create-trail \
  --name cosmic-watch-trail \
  --s3-bucket-name cosmic-watch-audit-logs \
  --region us-east-1
```

### 2. Enable VPC Flow Logs
```bash
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxxxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/cosmic-watch
```

### 3. Enable GuardDuty
```bash
aws guardduty create-detector --enable --region us-east-1
```

### 4. Set Up AWS Config
```bash
# Enable AWS Config for compliance monitoring
aws configservice put-config-recorder \
  --config-recorder roleARN=arn:aws:iam::ACCOUNT:role/... name=cosmic-watch-recorder
```

### 5. Enable S3 Encryption for Backups
```bash
aws s3api put-bucket-encryption \
  --bucket cosmic-watch-backups \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}
    }]
  }'
```

---

## Next Steps

1. Run the deployment script: `.\aws\deploy.ps1`
2. Set up SSL certificate via AWS Certificate Manager
3. Configure Route 53 for domain
4. Set up monitoring and alerts
5. Configure backup strategy
6. Test failover scenarios

---

**Setup complete! You're ready to deploy. 🚀**
