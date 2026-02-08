# Cosmic Watch - AWS Deployment Guide

**Status**: Production-ready  
**Platform**: AWS (ECS with Fargate)  
**Database**: Amazon RDS PostgreSQL  
**Cache**: Amazon ElastiCache Redis  
**Load Balancing**: Application Load Balancer (ALB)  
**CDN**: CloudFront (optional)  

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     CloudFront (CDN)                    │
│                   (Optional - S3 Static)                │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────┐
│            Application Load Balancer (ALB)              │
│              (Port 80 → 443, Route Paths)               │
└──────────────────────────┬──────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐  ┌──────────────┐
│ Frontend ECS │   │ Backend ECS  │  │ Backend ECS  │
│  (React App) │   │ (FastAPI)    │  │ (FastAPI)    │
│  Port 3000   │   │ Port 8000    │  │ Port 8000    │
└──────────────┘   └──────┬───────┘  └──────┬───────┘
                          │                  │
                   ┌──────┴──────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
     ┌────┐   ┌────────┐  ┌───────┐
     │RDS │   │ElastiC │  │Secrets│
     │PG  │   │ache    │  │Manager│
     └────┘   └────────┘  └───────┘
```

---

## Prerequisites

### 1. AWS Account Setup

1. **Create AWS Account**: https://aws.amazon.com
2. **Setup IAM User** with permissions for:
   - ECS, ECR, RDS, ElastiCache
   - ALB, VPC, EC2
   - CloudWatch, IAM
3. **Configure AWS CLI**:
   ```powershell
   # Windows PowerShell
   choco install awscli  # or install manually
   aws configure
   # Enter: Access Key ID, Secret Access Key, Region (e.g., us-east-1), Output (json)
   ```

### 2. Local Requirements

- Docker Desktop installed and running
- AWS CLI configured
- GitHub account (for CI/CD)
- Domain name (optional, use ALB DNS initially)

---

## Step 1: Create VPC and Security Groups

### 1.1 Create VPC (using CloudFormation or AWS Console)

```bash
# Using AWS CloudFormation (easier)
aws cloudformation create-stack \
  --stack-name cosmic-watch-vpc \
  --template-body file://vpc-template.yaml \
  --region us-east-1
```

Or manually via AWS Console:
1. Go to **VPC Dashboard** → **Create VPC**
2. Name: `cosmic-watch-vpc`, CIDR: `10.0.0.0/16`
3. Enable DNS hostnames

### 1.2 Create Subnets

**Public Subnets** (for ALB and NAT):
- `cosmic-watch-public-1a` (10.0.1.0/24, AZ: us-east-1a)
- `cosmic-watch-public-1b` (10.0.2.0/24, AZ: us-east-1b)

**Private Subnets** (for ECS, RDS, ElastiCache):
- `cosmic-watch-private-1a` (10.0.10.0/24, AZ: us-east-1a)
- `cosmic-watch-private-1b` (10.0.11.0/24, AZ: us-east-1b)

### 1.3 Create Security Groups

**ALB Security Group** (`alb-sg`):
```
Inbound Rules:
  - HTTP (80) from 0.0.0.0/0
  - HTTPS (443) from 0.0.0.0/0
Outbound: All traffic allowed
```

**ECS Security Group** (`ecs-sg`):
```
Inbound Rules:
  - Port 3000 from alb-sg (frontend)
  - Port 8000 from alb-sg (backend)
Outbound: All traffic allowed
```

**RDS Security Group** (`rds-sg`):
```
Inbound Rules:
  - PostgreSQL (5432) from ecs-sg
Outbound: All traffic allowed
```

**ElastiCache Security Group** (`redis-sg`):
```
Inbound Rules:
  - Redis (6379) from ecs-sg
Outbound: All traffic allowed
```

---

## Step 2: Create Database and Cache

### 2.1 Create RDS PostgreSQL Instance

**Via AWS Console**:
1. Go to **RDS Dashboard** → **Databases** → **Create database**
2. **Engine**: PostgreSQL 14.x (latest)
3. **Instance Class**: `db.t3.micro` (free tier eligible)
4. **Storage**: 20 GB, gp3
5. **DB Name**: `cosmic_watch_db`
6. **Username**: `cosmicwatch`
7. **Password**: Generate strong password (save to AWS Secrets Manager)
8. **VPC**: Select `cosmic-watch-vpc`
9. **Security Group**: Select `rds-sg`
10. **Backup**: 7 days retention
11. **Multi-AZ**: Yes (for production)
12. Create instance

**Connection String** (save this):
```
postgresql://cosmicwatch:PASSWORD@cosmic-watch-db.XXXXXXX.us-east-1.rds.amazonaws.com:5432/cosmic_watch_db
```

### 2.2 Create ElastiCache Redis Instance

**Via AWS Console**:
1. Go to **ElastiCache Dashboard** → **Clusters** → **Create cluster**
2. **Engine**: Redis, version 7.0
3. **Node type**: `cache.t3.micro`
4. **Nodes**: 1 (scale up for production)
5. **Subnet Group**: Create new in `cosmic-watch-vpc`
6. **Security Group**: Select `redis-sg`
7. **Backup**: Enable
8. Create cluster

**Connection String** (save this):
```
redis://cosmic-watch-redis.XXXXXXX.ng.0001.use1.cache.amazonaws.com:6379
```

### 2.3 Store Secrets in AWS Secrets Manager

```bash
# Store DB password
aws secretsmanager create-secret \
  --name cosmic-watch/db-password \
  --secret-string "YOUR_SECURE_PASSWORD" \
  --region us-east-1

# Store Redis URL
aws secretsmanager create-secret \
  --name cosmic-watch/redis-url \
  --secret-string "redis://HOST:6379" \
  --region us-east-1

# Store JWT secret
aws secretsmanager create-secret \
  --name cosmic-watch/jwt-secret \
  --secret-string "YOUR_JWT_SECRET_KEY" \
  --region us-east-1
```

---

## Step 3: Setup Amazon ECR (Container Registry)

### 3.1 Create ECR Repositories

```bash
# Backend repository
aws ecr create-repository \
  --repository-name cosmic-watch/backend \
  --region us-east-1

# Frontend repository
aws ecr create-repository \
  --repository-name cosmic-watch/frontend \
  --region us-east-1
```

### 3.2 Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t cosmic-watch/backend:latest .
docker tag cosmic-watch/backend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/backend:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/backend:latest

# Build and push frontend
cd ../frontend
docker build -t cosmic-watch/frontend:latest .
docker tag cosmic-watch/frontend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/frontend:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/frontend:latest
```

Replace `ACCOUNT_ID` with your AWS Account ID (get it from `aws sts get-caller-identity`).

---

## Step 4: Create ECS Cluster and Services

### 4.1 Create ECS Cluster

```bash
aws ecs create-cluster \
  --cluster-name cosmic-watch-cluster \
  --region us-east-1
```

### 4.2 Create Task Definitions

See `ecs-task-definitions.json` file for complete definitions.

```bash
# Backend task definition
aws ecs register-task-definition \
  --cli-input-json file://backend-task-definition.json \
  --region us-east-1

# Frontend task definition
aws ecs register-task-definition \
  --cli-input-json file://frontend-task-definition.json \
  --region us-east-1
```

### 4.3 Create ECS Services

```bash
# Backend service
aws ecs create-service \
  --cluster cosmic-watch-cluster \
  --service-name cosmic-watch-backend \
  --task-definition cosmic-watch-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXX,subnet-YYYY],securityGroups=[sg-XXXX],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=backend,containerPort=8000" \
  --region us-east-1

# Frontend service
aws ecs create-service \
  --cluster cosmic-watch-cluster \
  --service-name cosmic-watch-frontend \
  --task-definition cosmic-watch-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-XXXX,subnet-YYYY],securityGroups=[sg-XXXX],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=frontend,containerPort=3000" \
  --region us-east-1
```

---

## Step 5: Setup Application Load Balancer

### 5.1 Create ALB

```bash
aws elbv2 create-load-balancer \
  --name cosmic-watch-alb \
  --subnets subnet-XXXX subnet-YYYY \
  --security-groups sg-XXXX \
  --scheme internet-facing \
  --type application \
  --region us-east-1
```

### 5.2 Create Target Groups

```bash
# Backend target group
aws elbv2 create-target-group \
  --name cosmic-watch-backend \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-XXXX \
  --target-type ip \
  --region us-east-1

# Frontend target group
aws elbv2 create-target-group \
  --name cosmic-watch-frontend \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-XXXX \
  --target-type ip \
  --region us-east-1
```

### 5.3 Create Listeners

```bash
# HTTP listener (redirects to HTTPS)
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=redirect,RedirectConfig="{Protocol=HTTPS,Port=443,StatusCode=HTTP_301}" \
  --region us-east-1

# HTTPS listener (requires SSL certificate)
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:.../frontend \
  --region us-east-1
```

### 5.4 Create Listener Rules

```bash
# Route /api to backend
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:... \
  --conditions Field=path-pattern,Values="/api/*" \
  --priority 1 \
  --actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:.../backend \
  --region us-east-1
```

---

## Step 6: Setup SSL/TLS Certificate

### 6.1 Request ACM Certificate

```bash
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names www.yourdomain.com \
  --region us-east-1
```

### 6.2 Validate Certificate

1. Check your email for validation link
2. Click the link to approve certificate
3. Certificate status will show "Issued"

---

## Step 7: Scale and Auto-scaling

### 7.1 Create Auto Scaling Group for Backend

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name cosmic-watch-backend-asg \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2 \
  --vpc-zone-identifier "subnet-XXXX,subnet-YYYY" \
  --region us-east-1
```

### 7.2 Create Scaling Policy

```bash
# Scale up when CPU > 70%
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name cosmic-watch-backend-asg \
  --policy-name scale-up \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration "TargetValue=70.0,PredefinedMetricSpecification={PredefinedMetricType=ASGAverageCPUUtilization}" \
  --region us-east-1
```

---

## Step 8: Monitor and Logging

### 8.1 CloudWatch Logs

Logs automatically stream from ECS to CloudWatch. View them:

```bash
# View backend logs
aws logs tail /ecs/cosmic-watch-backend --follow --region us-east-1

# View frontend logs
aws logs tail /ecs/cosmic-watch-frontend --follow --region us-east-1
```

### 8.2 CloudWatch Alarms

```bash
# Alert on high CPU
aws cloudwatch put-metric-alarm \
  --alarm-name cosmic-watch-backend-cpu \
  --alarm-description "Alert when backend CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 60 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --region us-east-1
```

---

## Step 9: Environment Variables Setup

### Backend `.env` (via Secrets Manager or ECS environment)

```env
DATABASE_URL=postgresql://cosmicwatch:PASSWORD@cosmic-watch-db.XXXXXXX.us-east-1.rds.amazonaws.com:5432/cosmic_watch_db
REDIS_URL=redis://cosmic-watch-redis.XXXXXXX.ng.0001.use1.cache.amazonaws.com:6379
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
ENVIRONMENT=production
```

### Frontend `.env` (build-time or runtime)

```env
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_APP_NAME=Cosmic Watch
VITE_APP_VERSION=1.0.0
```

---

## Step 10: Domain Setup

### 10.1 Using Route 53

```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name yourdomain.com \
  --caller-reference $(date +%s) \
  --region us-east-1

# Point to ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://route53-changes.json
```

### 10.2 Route53 Changes JSON

Create `route53-changes.json`:
```json
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z1H1FL5HABSF5",
          "DNSName": "cosmic-watch-alb-123456.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}
```

---

## Step 11: Run Database Migrations

```bash
# SSH into backend container or use ECS Exec
aws ecs execute-command \
  --cluster cosmic-watch-cluster \
  --task cosmic-watch-backend-XXXXX \
  --container backend \
  --interactive \
  --command "/bin/sh"

# Inside container:
cd /app
alembic upgrade head
```

---

## Cost Estimation (Monthly)

| Service | Size | Estimated Cost |
|---------|------|-----------------|
| ECS Fargate (backend) | 2x 0.25 CPU, 512 MB RAM | $25 |
| ECS Fargate (frontend) | 2x 0.25 CPU, 512 MB RAM | $25 |
| RDS PostgreSQL | db.t3.micro | $20 |
| ElastiCache Redis | cache.t3.micro | $15 |
| ALB | 1 ALB, 1M requests | $20 |
| Data Transfer | ~100 GB out | $10 |
| **Total** | | **~$115/month** |

---

## Troubleshooting

### Tasks won't start
```bash
# Check task definition
aws ecs describe-task-definition --task-definition cosmic-watch-backend --region us-east-1

# Check task logs
aws logs tail /ecs/cosmic-watch-backend --follow --region us-east-1
```

### Database connection errors
```bash
# Verify security group rules
aws ec2 describe-security-groups --group-ids sg-XXXX --region us-east-1

# Test connection
psql -h cosmic-watch-db.XXXXXXX.us-east-1.rds.amazonaws.com -U cosmicwatch -d cosmic_watch_db
```

### ALB health checks failing
1. Check target group health: **EC2 Dashboard** → **Target Groups**
2. Verify security groups allow communication
3. Check service logs: `aws logs tail /ecs/cosmic-watch-backend`

---

## Next Steps

1. **Setup CI/CD**: Use GitHub Actions to auto-deploy on push
2. **Enable CloudFront**: Cache static assets globally
3. **Setup CloudWatch Dashboards**: Monitor real-time metrics
4. **Enable VPC Endpoints**: Secure communication with AWS services
5. **Implement Backup Strategy**: RDS automated backups + snapshots

---

## Cleanup (Delete all resources)

```bash
# Delete ECS services
aws ecs delete-service --cluster cosmic-watch-cluster --service cosmic-watch-backend --force

# Delete ECS cluster
aws ecs delete-cluster --cluster cosmic-watch-cluster

# Delete ALB
aws elbv2 delete-load-balancer --load-balancer-arn arn:aws:elasticloadbalancing:...

# Delete RDS
aws rds delete-db-instance --db-instance-identifier cosmic-watch-db --skip-final-snapshot

# Delete ElastiCache
aws elasticache delete-cache-cluster --cache-cluster-id cosmic-watch-redis

# Delete VPC
aws ec2 delete-vpc --vpc-id vpc-XXXX
```

---

**Need Help?** Check the AWS Management Console or enable CloudTrail for detailed error logs.
