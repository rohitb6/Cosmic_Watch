# AWS Deployment Directory

This directory contains everything needed to deploy Cosmic Watch on AWS using Infrastructure as Code.

## 📁 Directory Structure

```
aws/
├── README.md                      # This file
├── QUICKSTART.md                  # 15-minute quick start guide
├── ENVIRONMENT_SETUP.md           # Prerequisites and setup instructions
├── MONITORING_GUIDE.md            # CloudWatch, alarms, scaling, troubleshooting
├── COST_OPTIMIZATION.md           # Cost optimization strategies
├── cloudformation-template.yaml   # Complete IaC definition
├── deploy.sh                      # Bash deployment script (Linux/macOS)
├── deploy.ps1                     # PowerShell deployment script (Windows)
├── dashboards/                    # CloudWatch dashboard definitions
│   ├── backend-dashboard.json
│   ├── frontend-dashboard.json
│   └── infrastructure-dashboard.json
└── config/                        # Configuration templates
    ├── .env.template
    ├── ecs-task-definitions.json
    └── alb-routing-rules.json
```

## 🚀 Quick Start

```bash
cd aws

# Windows (PowerShell)
.\deploy.ps1 -Environment production

# Linux/macOS (Bash)
bash deploy.sh production
```

**Time to deployment: 15-20 minutes**

## 📚 Documentation Files

### 1. [QUICKSTART.md](QUICKSTART.md)
- 15-minute deployment guide
- Step-by-step instructions
- Troubleshooting quick fixes
- Common tasks reference

### 2. [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- Prerequisites installation
- AWS account setup
- IAM user creation
- Environment variables configuration
- Secrets Manager setup
- GitHub Actions OIDC setup

### 3. [MONITORING_GUIDE.md](MONITORING_GUIDE.md)
- CloudWatch logs and dashboards
- Setting up alarms
- Auto-scaling configuration
- Troubleshooting guide
- Performance optimization
- Backup & disaster recovery

### 4. [COST_OPTIMIZATION.md](COST_OPTIMIZATION.md)
- Cost breakdown
- Optimization strategies
- Right-sizing recommendations
- Savings plans
- Monitoring and alerts
- Scaling for growth

## 🏗️ Infrastructure Components

### Compute
- **ECS Fargate**: Container orchestration
- **Task Definitions**: Backend and frontend container specifications
- **Auto Scaling**: Automatic scaling based on CPU/memory

### Database & Cache
- **RDS PostgreSQL**: Managed relational database
- **ElastiCache Redis**: In-memory cache for sessions & performance

### Networking
- **VPC**: Custom virtual private cloud
- **Application Load Balancer**: Traffic distribution
- **Security Groups**: Network access control
- **NAT Gateway**: Outbound internet access for private resources

### Images & Artifacts
- **ECR**: Container image registry
- **Secrets Manager**: Secure credential storage

### Monitoring
- **CloudWatch**: Logs, metrics, dashboards
- **Alarms**: Automated alerting

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] AWS account created with billing set up
- [ ] IAM user created with appropriate permissions
- [ ] AWS CLI installed and configured
- [ ] Docker installed and running
- [ ] Git cloned and repository ready
- [ ] Environment variables prepared
- [ ] Secrets created in Secrets Manager

### Deployment
- [ ] Run deployment script (`deploy.sh` or `deploy.ps1`)
- [ ] CloudFormation stack creation in progress
- [ ] Monitor stack events for errors
- [ ] Wait for all resources to be created (10-15 minutes)
- [ ] Verify RDS, ElastiCache, and ECS are running

### Post-Deployment
- [ ] Retrieve ALB DNS name
- [ ] Test application health endpoints
- [ ] Run database migrations
- [ ] Verify application functionality
- [ ] Setup custom domain (Route 53)
- [ ] Request SSL certificate (ACM)
- [ ] Update ALB listener for HTTPS
- [ ] Configure CloudWatch alarms
- [ ] Enable auto-scaling policies
- [ ] Setup CI/CD pipeline (GitHub Actions)

### Production Hardening
- [ ] Enable CloudTrail
- [ ] Enable VPC Flow Logs
- [ ] Enable GuardDuty
- [ ] Configure backup retention
- [ ] Setup disaster recovery plan
- [ ] Document runbooks
- [ ] Test failover scenarios
- [ ] Configure SSO/SAML (if applicable)

## 🔧 Deployment Scripts

### PowerShell (Windows)
```powershell
.\deploy.ps1 -Environment production -AWSRegion us-east-1
```

**Features:**
- Validates prerequisites
- Creates secrets securely
- Builds and pushes Docker images
- Deploys CloudFormation stack
- Displays deployment summary

### Bash (Linux/macOS)
```bash
chmod +x deploy.sh
./deploy.sh production
```

**Features:**
- Same functionality as PowerShell
- BASH-specific optimizations
- Supports multiple AWS regions

## 📦 CloudFormation Template

The `cloudformation-template.yaml` is a complete Infrastructure as Code definition that creates:

1. **VPC with public/private subnets** (2 availability zones)
2. **NAT Gateway** for outbound internet access
3. **Security groups** for ALB, ECS, RDS, and Redis
4. **RDS PostgreSQL** database instance
5. **ElastiCache Redis** cluster
6. **ECR repositories** for backend and frontend
7. **ECS cluster** with task definitions for both services
8. **Application Load Balancer** with routing rules
9. **CloudWatch log groups** for logging
10. **IAM roles** for ECS task execution
11. **Auto Scaling** policies for backend service

**Template Size:** ~1000 lines of YAML

## 🌐 Architecture Diagram

```
Internet
    ↓
┌─────────────────────────────────────────┐
│        Route 53 (DNS)                   │
│        [yourdomain.com]                 │
└──────────────────┬──────────────────────┘
                   ↓
         ┌─────────────────────┐
         │  CloudFront (CDN)   │  ← Optional: cache static assets
         │   (Optional)        │
         └──────────┬──────────┘
                    ↓
    ┌───────────────────────────────┐
    │ Application Load Balancer     │
    │ (ALB - Port 80/443)          │
    └───────────────────────────────┘
           ↑              ↓
           │              │
     ┌─────────────────────────────┐
     │    Path-based Routing       │
     │ /      → Frontend           │
     │ /api   → Backend            │
     └─────────────────────────────┘
           ↑              ↓
      ┌────────┐     ┌────────┐
      │Frontend │     │Backend │
      │ ECS Srv │     │ ECS Srv│
      │ (Port  │     │ (Port │
      │ 3000)  │     │ 8000) │
      └────────┘     └────────┘
           ↑              ↓
      ┌─────────────────────────┐
      │    RDS PostgreSQL       │
      │  (Port 5432)            │
      │  cosmic_watch_db        │
      └─────────────────────────┘
      
      ┌─────────────────────────┐
      │  ElastiCache Redis      │
      │  (Port 6379)            │
      │  Session & Cache Store  │
      └─────────────────────────┘
```

## 🔐 Security Architecture

- **Network Security**: VPC isolation, security groups, NACLs
- **Data Protection**: RDS encryption, SSL/TLS, Secrets Manager
- **Access Control**: IAM roles, least privilege permissions
- **Monitoring**: CloudTrail, VPC Flow Logs, GuardDuty
- **Secrets**: AWS Secrets Manager for database credentials, JWT keys
- **Encryption**: KMS for encryption key management (optional)

## 💻 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET_KEY=...
CORS_ORIGINS=[...]
ENVIRONMENT=production
```

### Frontend (Build-time)
```env
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_APP_NAME=Cosmic Watch
VITE_APP_VERSION=1.0.0
```

See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for complete list.

## 📊 Monitoring & Observability

- **CloudWatch Logs**: Centralized logging from ECS
- **CloudWatch Metrics**: CPU, memory, request count
- **CloudWatch Alarms**: Automated alerts for problems
- **CloudWatch Dashboards**: Visual monitoring
- **X-Ray** (optional): Distributed tracing

## 🚀 CI/CD Integration

### GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/deploy-aws.yml`) that:

1. Builds Docker images
2. Pushes to ECR
3. Updates ECS services
4. Monitors deployment progress
5. Sends notifications

**Setup required:**
- Add secrets to GitHub repository
- Configure AWS OIDC trust relationship

## 📚 Additional Resources

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/)
- [ElastiCache Documentation](https://docs.aws.amazon.com/elasticache/)
- [CloudFormation User Guide](https://docs.aws.amazon.com/cloudformation/)
- [AWS Security Best Practices](https://aws.amazon.com/architecture/security-identity-compliance/)

## ❓ Troubleshooting

### CloudFormation Stack Creation Fails
```bash
# Check stack events
aws cloudformation describe-stack-events \
  --stack-name production-cosmic-watch-stack
```

### Tasks Won't Start
```bash
# Check logs
aws logs tail /ecs/production-cosmic-watch-backend --follow
```

### Database Connection Issues
```bash
# Verify security groups
aws ec2 describe-security-groups --group-ids sg-xxx
```

See [MONITORING_GUIDE.md](MONITORING_GUIDE.md) for more troubleshooting steps.

## 💰 Cost

- **Estimated Monthly Cost**: $113 (development setup)
- **Enterprise Setup**: $400-500+ (with redundancy)

See [COST_OPTIMIZATION.md](COST_OPTIMIZATION.md) for detailed breakdown and optimization strategies.

## 🤝 Support

- **AWS Support**: Contact AWS Support (Business plan recommended for production)
- **Community**: [AWS Forums](https://forums.aws.amazon.com/)
- **Documentation**: [AWS Docs](https://docs.aws.amazon.com/)

## 📝 License

This deployment configuration is part of Cosmic Watch.
See [LICENSE.md](../LICENSE.md) for details.

---

**Ready to deploy? Start with the [QUICKSTART.md](QUICKSTART.md)! 🚀**
