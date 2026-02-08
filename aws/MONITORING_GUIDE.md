# AWS Monitoring, Scaling & Troubleshooting Guide

## 📊 CloudWatch Monitoring

### 1. View Application Logs

```bash
# Backend logs
aws logs tail /ecs/production-cosmic-watch-backend --follow

# Frontend logs
aws logs tail /ecs/production-cosmic-watch-frontend --follow

# Filter logs by level
aws logs filter-log-events \
  --log-group-name /ecs/production-cosmic-watch-backend \
  --filter-pattern "ERROR" \
  --start-time $(date -d '1 hour ago' +%s)000

# Get specific log streams
aws logs describe-log-streams \
  --log-group-name /ecs/production-cosmic-watch-backend \
  --order-by LastEventTime \
  --descending \
  --max-items 5
```

### 2. Create CloudWatch Dashboards

```bash
# Backend service dashboard
aws cloudwatch put-dashboard \
  --dashboard-name cosmic-watch-backend \
  --dashboard-body file://dashboards/backend-dashboard.json

# Frontend service dashboard
aws cloudwatch put-dashboard \
  --dashboard-name cosmic-watch-frontend \
  --dashboard-body file://dashboards/frontend-dashboard.json

# Infrastructure dashboard
aws cloudwatch put-dashboard \
  --dashboard-name cosmic-watch-infrastructure \
  --dashboard-body file://dashboards/infrastructure-dashboard.json
```

### 3. Setup CloudWatch Alarms

**CPU Utilization:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name cosmic-watch-backend-high-cpu \
  --alarm-description "Alert when backend CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ServiceName,Value=production-cosmic-watch-backend Name=ClusterName,Value=production-cosmic-watch-cluster \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:cosmic-watch-alerts
```

**Memory Utilization:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name cosmic-watch-backend-high-memory \
  --alarm-description "Alert when backend memory > 85%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ServiceName,Value=production-cosmic-watch-backend Name=ClusterName,Value=production-cosmic-watch-cluster \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:cosmic-watch-alerts
```

**Unhealthy Task Count:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name cosmic-watch-unhealthy-tasks \
  --alarm-description "Alert when unhealthy tasks > 0" \
  --metric-name RunningCount \
  --namespace AWS/ECS \
  --statistic Minimum \
  --period 300 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=ServiceName,Value=production-cosmic-watch-backend Name=ClusterName,Value=production-cosmic-watch-cluster \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:cosmic-watch-alerts
```

**RDS Connection Count:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name cosmic-watch-rds-high-connections \
  --alarm-description "Alert when RDS connections > 90% of max" \
  --metric-name DatabaseConnections \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 90 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=production-cosmic-watch-db \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:cosmic-watch-alerts
```

**ALB Target Health:**
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name cosmic-watch-alb-unhealthy-hosts \
  --alarm-description "Alert when ALB has unhealthy targets" \
  --metric-name UnHealthyHostCount \
  --namespace AWS/ApplicationELB \
  --statistic Maximum \
  --period 60 \
  --threshold 0 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:cosmic-watch-alerts
```

---

## 🔄 Auto Scaling Configuration

### 1. Setup Auto Scaling for Backend

```bash
# Register scalable target
aws autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/production-cosmic-watch-cluster/production-cosmic-watch-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# CPU-based scaling policy (scale out at 70%)
aws autoscaling put-scaling-policy \
  --policy-name cosmic-watch-backend-cpu-scaling \
  --service-namespace ecs \
  --resource-id service/production-cosmic-watch-cluster/production-cosmic-watch-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    TargetValue=70.0,PredefinedMetricSpecification={PredefinedMetricType=ECSServiceAverageCPUUtilization}

# Memory-based scaling policy (scale out at 80%)
aws autoscaling put-scaling-policy \
  --policy-name cosmic-watch-backend-memory-scaling \
  --service-namespace ecs \
  --resource-id service/production-cosmic-watch-cluster/production-cosmic-watch-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    TargetValue=80.0,PredefinedMetricSpecification={PredefinedMetricType=ECSServiceAverageMemoryUtilization}
```

### 2. RDS Auto Scaling (Read Replicas)

```bash
# Create read replica for failover
aws rds create-db-instance-read-replica \
  --db-instance-identifier production-cosmic-watch-db-replica \
  --source-db-instance-identifier production-cosmic-watch-db \
  --availability-zone us-east-1b \
  --auto-minor-version-upgrade
```

### 3. ElastiCache Multi-AZ

```bash
# Update Redis cluster to multi-AZ
aws elasticache modify-cache-cluster \
  --cache-cluster-id production-cosmic-watch-redis \
  --automatic-failover-enabled
```

---

## 🔍 Troubleshooting Guide

### Issue 1: Tasks Won't Start

```bash
# Check task status
aws ecs describe-tasks \
  --cluster production-cosmic-watch-cluster \
  --tasks arn:aws:ecs:...

# Common causes:
# 1. Image not found
docker images | grep cosmic-watch
aws ecr describe-images --repository-name cosmic-watch/backend

# 2. Insufficient memory/CPU
aws ecs describe-container-instances \
  --cluster production-cosmic-watch-cluster

# 3. Port conflicts
aws ec2 describe-network-interface-attribute \
  --network-interface-id eni-xxxxx \
  --attribute groupSet

# Solution: Check and update task definition
aws ecs describe-task-definition \
  --task-definition production-cosmic-watch-backend:latest
```

### Issue 2: Database Connection Errors

```bash
# Verify RDS is running
aws rds describe-db-instances \
  --db-instance-identifier production-cosmic-watch-db

# Test connectivity from EC2
psql -h production-cosmic-watch-db.XXXXX.us-east-1.rds.amazonaws.com \
  -U cosmicwatch \
  -d cosmic_watch_db \
  -c "SELECT 1"

# Check security groups
aws ec2 describe-security-groups \
  --group-ids sg-XXXXX \
  --query 'SecurityGroups[0].IpPermissions'

# Check network ACLs
aws ec2 describe-network-acls \
  --filters "Name=association.subnet-id,Values=subnet-XXXXX"
```

### Issue 3: ALB Health Checks Failing

```bash
# Check target health
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# Test backend endpoint directly
curl -v http://TASK_IP:8000/health

# Check ALB security group
aws ec2 describe-security-groups \
  --group-ids sg-alb

# Verify health check path and port
aws elbv2 describe-target-groups \
  --target-group-arns arn:aws:elasticloadbalancing:...
```

### Issue 4: High Memory Usage

```bash
# Check container memory usage
docker stats

# Check process memory
top -b -n 1 | head -20

# Get memory metrics from CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=production-cosmic-watch-backend \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average,Maximum

# Solutions:
# 1. Increase task memory in task definition
# 2. Optimize code for memory leaks
# 3. Add caching layer
```

### Issue 5: High CPU Usage

```bash
# Check CPU metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=production-cosmic-watch-backend \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average,Maximum

# Profile application
python -m cProfile -o profile.prof main.py

# Solutions:
# 1. Increase task CPU
# 2. Optimize slow queries
# 3. Add caching
# 4. Enable auto-scaling
```

---

## 📈 Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_asteroid_hazard ON asteroids(hazard_score);
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_alert_user ON alerts(user_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM asteroids WHERE hazard_score > 0.7;

-- Vacuum to optimize storage
VACUUM ANALYZE;
```

### 2. Redis Caching

```python
# Cache frequently accessed data
cache.set("asteroids:high_hazard", asteroids, timeout=3600)

# Cache user data
cache.set(f"user:{user_id}:watchlist", watchlist, timeout=1800)

# Monitor cache hit rate
INFO stats
```

### 3. Frontend Optimization

```bash
# Enable compression (ALB)
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --attributes Key=decompression.enabled,Value=true

# Add CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name ALB_DNS_NAME \
  --default-root-object index.html
```

---

## 🔄 Backup & Disaster Recovery

### 1. RDS Backups

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier production-cosmic-watch-db \
  --db-snapshot-identifier backup-$(date +%Y%m%d)

# List backups
aws rds describe-db-snapshots \
  --db-instance-identifier production-cosmic-watch-db

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier production-cosmic-watch-db-restored \
  --db-snapshot-identifier backup-20240101
```

### 2. Redis Backup

```bash
# Automatic backup (enabled by default)
aws elasticache describe-snapshots \
  --cache-cluster-id production-cosmic-watch-redis

# Create manual snapshot
aws elasticache create-snapshot \
  --cache-cluster-id production-cosmic-watch-redis \
  --snapshot-name manual-backup-$(date +%Y%m%d)
```

### 3. Application Code Backup

```bash
# Create ECR image backup
docker tag ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/backend:latest \
           ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/backend:backup-$(date +%Y%m%d)

docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch/backend:backup-$(date +%Y%m%d)
```

---

## 📊 Common Metrics to Monitor

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| CPU Utilization | 50-70% | > 80% | > 90% |
| Memory Utilization | 60-75% | > 85% | > 95% |
| Database Connections | < 50% of max | > 80% | > 95% |
| Request Latency | < 200ms | > 500ms | > 1000ms |
| Error Rate | < 0.1% | > 1% | > 5% |
| Requests/sec | Varies | Monitor trend | Spike > 2x |

---

**Monitor regularly and adjust thresholds based on your application's baseline! 📈**
