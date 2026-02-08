# AWS Cost Optimization Guide

## 💰 Cost Breakdown

### Current Architecture Costs (Monthly)

| Component | Configuration | Estimated Cost |
|-----------|---------------|-----------------|
| **ECS Fargate (Backend)** | 2 tasks × 256 CPU, 512 MB RAM | $25 |
| **ECS Fargate (Frontend)** | 2 tasks × 256 CPU, 512 MB RAM | $25 |
| **RDS PostgreSQL** | db.t3.micro, 20 GB, Multi-AZ | $20 |
| **ElastiCache Redis** | cache.t3.micro, single node | $12 |
| **Application Load Balancer** | 1 ALB, ~1M requests | $16 |
| **Data Transfer** | ~100 GB outbound | $9 |
| **CloudWatch** | Logs, metrics, alarms | $5 |
| **ECR Storage** | ~1 GB images | $1 |
| **Total Monthly** | | **~$113** |

### Cost by Environment

```
Development: ~$50/month
Staging: ~$80/month
Production: ~$130/month (with redundancy & failover)
```

---

## 🎯 Cost Optimization Strategies

### 1. Right-Sizing Compute

**Current vs Optimized:**

```bash
# Check actual usage
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=production-cosmic-watch-backend \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T00:00:00Z \
  --period 86400 \
  --statistics Average,Maximum

# If CPU < 30% consistently, reduce to 128 CPU
# If memory < 256 MB, reduce task memory
```

**Recommendations:**
- **Low Traffic**: Use 128 CPU, 256 MB RAM (saves $15/month)
- **Medium Traffic**: Use 256 CPU, 512 MB RAM (current)
- **High Traffic**: Use 512 CPU, 1 GB RAM (or scale horizontally)

### 2. Reserved Capacity Discounts

```bash
# Purchase 1-year reserved capacity (28% discount)
aws ec2 purchase-reserved-instances \
  --instance-count 1 \
  --instance-type t3.small \
  --offering-class standard \
  --purchase-type one-year

# For ECS Fargate, use Fargate Savings Plans
# 1-year commitment: 20% discount
# 3-year commitment: 34% discount
```

**Savings:**
- 1-year commitment: ~$32/month savings
- 3-year commitment: ~$44/month savings

### 3. Database Optimization

**Use Smaller Instance for Dev:**
```bash
# Development SQL: micro (1-2 GB, ~$10/month)
# Production: t3.small (2-4 GB, ~$20/month) with read replicas
```

**Enable Multi-AZ Only for Production:**
```bash
# Non-production: ~$15/month (single AZ)
# Production: ~$30/month (Multi-AZ)
```

**RDS Storage Optimization:**
```bash
# Monitor actual storage usage
aws rds describe-db-instances \
  --db-instance-identifier production-cosmic-watch-db \
  --query 'DBInstances[0].AllocatedStorage'

# Optimize to actual needs (currently 20 GB, may reduce to 10 GB)
```

### 4. Cache Optimization

**Development/Staging:**
```bash
# Use cache.t2.micro instead of cache.t3.micro (~$10/month vs $15/month)
aws elasticache modify-cache-cluster \
  --cache-cluster-id staging-cosmic-watch-redis \
  --cache-node-type cache.t2.micro
```

**Production:**
```bash
# Single node: $15/month
# Multi-node cluster: $35/month (skip unless high traffic)
```

### 5. Network Cost Optimization

**Reduce Data Transfer:**

```bash
# Enable ALB compression
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --attributes Key=decompression.enabled,Value=true

# Use CloudFront for static assets (~$1-5/month additional, saves $5-10 in transfer)
aws cloudfront create-distribution \
  --origin-domain-name ALB_DNS \
  --default-cache-behavior file://cloudfront-config.json
```

**VPC Data Transfer:**
- Use NAT gateway in 1 AZ instead of 2 (saves ~$15/month)
- Use VPC endpoints for AWS services (saves data transfer costs)

### 6. Storage Optimization

**S3 Backup Storage:**
```bash
# Use S3 Intelligent-Tiering
# Automatically moves old files to cheaper tiers
aws s3api put-bucket-intelligent-tiering-configuration \
  --bucket cosmic-watch-backups \
  --id AutoTransition \
  --intelligent-tiering-configuration file://tiering-config.json
```

---

## 📊 Optimized Architecture (Lower Cost)

### Development Environment (~$30/month)

```yaml
ECS:
  - Backend: 128 CPU, 256 MB RAM × 1 instance
  - Frontend: 128 CPU, 256 MB RAM × 1 instance
Database:
  - db.t3.micro, single AZ, 10 GB storage
Cache:
  - cache.t2.micro, single node
Load Balancer:
  - Shared ALB ($5/month)
```

### Production Environment (~$85/month with optimizations)

```yaml
ECS:
  - Backend: 256 CPU, 512 MB RAM × 2 instances
  - Frontend: 256 CPU, 512 MB RAM × 2 instances
  - Auto-scaling: 2-6 instances (scales based on load)
Database:
  - db.t3.small, single AZ (not Multi-AZ for cost), 10 GB storage
Cache:
  - cache.t3.micro, single node
Load Balancer:
  - Dedicated ALB ($16/month)
CloudFront:
  - For static assets ($1-5/month)
```

**Savings: ~$45/month**

---

## 🔄 Cost Monitoring & Alerts

### 1. Setup Billing Alerts

```bash
# Alert when bill exceeds $150/month
aws cloudwatch put-metric-alarm \
  --alarm-name cosmic-watch-monthly-bill-alert \
  --alarm-description "Alert when monthly bill exceeds $150" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 86400 \
  --threshold 150 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD
```

### 2. AWS Cost Explorer

```bash
# View costs by service
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE
```

### 3. Tagging for Cost Allocation

```bash
# Tag all resources for cost tracking
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Environment,Value=production Key=Project,Value=cosmic-watch

# View costs by tag
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --group-by Type=TAG,Key=Environment
```

---

## 🎁 AWS Free Tier & Credits

Check if you're eligible:

```bash
# AWS Free Tier (1 year, always free within limits)
# - t2/t3 micro instances: 750 hours/month
# - RDS Single-AZ: 750 hours/month, db.t2.micro
# - Load Balancer: Free for 1 ALB usage, limited data
# - Data Transfer: 1 GB/month free

# Estimated free tier value: ~$30-40/month

# Apply for AWS credits (startups, students, etc.)
# https://aws.amazon.com/activate/ (for startups)
# https://www.awseducate.com/ (for students)
```

---

## 📈 Scaling for Growth

### Phase 1: MVP (~$113/month)
- 2 backend tasks, 2 frontend tasks
- db.t3.micro database
- Single Redis node
- No auto-scaling

### Phase 2: Growing (200+ users, ~$250/month)
- Auto-scaling backend (2-6 instances)
- db.t3.small database with read replica
- Redis cluster
- CloudFront CDN
- Enhanced monitoring

### Phase 3: Enterprise (~$500+/month)
- Multi-region deployment
- RDS Multi-AZ + read replicas
- Redis cluster with failover
- DynamoDB for caching
- Global CDN
- Enhanced security & compliance

---

## 💡 Optimization Checklist

- [ ] Right-size ECS tasks based on actual CPU/memory usage
- [ ] Use spot instances (not available for Fargate) or Compute Savings Plans
- [ ] Enable Savings Plans for 1-year or 3-year commitments
- [ ] Reduce database instance from db.t3.micro to db.t3.small for non-prod
- [ ] Use cache.t2.micro instead of cache.t3.micro
- [ ] Implement VPC endpoints to reduce NAT gateway costs
- [ ] Enable CloudFront for static assets
- [ ] Compress API responses (gzip)
- [ ] Implement query optimization in database
- [ ] Set up billing alerts
- [ ] Tag all resources for cost allocation
- [ ] Review Reserved Instances pricing annually
- [ ] Monitor CloudWatch logs retention (7 days is default)
- [ ] Use S3 Intelligent-Tiering for backups
- [ ] Configure auto-scaling policies to avoid over-provisioning

---

## 📞 Getting Help

- **AWS Cost Optimizer**: https://console.aws.amazon.com/cost-management/home
- **AWS Pricing Calculator**: https://calculator.aws/
- **AWS Trusted Advisor**: https://console.aws.amazon.com/trustedadvisor/
- **AWS Support**: AWS Support plans available (Business, Enterprise)

---

**Optimize continuously and monitor your costs! 📉**
