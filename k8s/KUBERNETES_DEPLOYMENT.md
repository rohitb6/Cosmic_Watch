# Kubernetes Deployment Guide

## Overview

This guide covers deploying Cosmic Watch to a Kubernetes cluster (EKS, GKE, AKS, or self-hosted).

## Prerequisites

- Kubernetes 1.24+ cluster running
- `kubectl` CLI configured
- Helm 3.x (optional, for package management)
- Container registry (Docker Hub, GitHub Container Registry, ECR, GCR)
- Docker images built and pushed

## Quick Start (5 minutes)

### 1. Set Up Namespace and Secrets

```bash
# Create namespace
kubectl create namespace cosmic-watch

# Create secrets (IMPORTANT: replace values!)
kubectl create secret generic cosmic-watch-secrets \
  --from-literal=DATABASE_URL='postgresql://cosmicwatch:YOUR_DB_PASSWORD@postgres:5432/cosmic_watch_db' \
  --from-literal=REDIS_URL='redis://redis:6379/0' \
  --from-literal=SECRET_KEY='your-secure-random-key-here' \
  --from-literal=NASA_API_KEY='your-nasa-api-key' \
  --from-literal=OPENAI_API_KEY='your-openai-api-key' \
  --from-literal=DB_PASSWORD='YOUR_DB_PASSWORD' \
  -n cosmic-watch
```

### 2. Update Image References

Edit `deployment.yaml` and replace image references:

```yaml
# Old:
image: ghcr.io/yourusername/cosmic-watch-backend:latest

# New:
image: ghcr.io/your-actual-username/cosmic-watch-backend:v1.0.0
```

Or use a sed command:

```bash
sed -i 's|ghcr.io/yourusername|ghcr.io/your-actual-username|g' k8s/deployment.yaml
sed -i 's|:latest|:v1.0.0|g' k8s/deployment.yaml
```

### 3. Deploy to Cluster

```bash
# Apply all manifests
kubectl apply -f k8s/

# Verify deployments
kubectl get deployments -n cosmic-watch
kubectl get pods -n cosmic-watch
kubectl get services -n cosmic-watch

# Check pod status
kubectl describe pod <pod-name> -n cosmic-watch

# View logs
kubectl logs <pod-name> -n cosmic-watch
```

### 4. Configure Ingress

For AWS EKS:
```bash
# Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=my-cluster
```

For GKE:
```bash
# GKE has ingress built-in, just configure DNS
gcloud compute addresses create cosmic-watch-ip --global
```

### 5. Update DNS

Point your domain to the LoadBalancer IP:

```bash
# Get LoadBalancer IP/hostname
kubectl get ingress cosmic-watch -n cosmic-watch

# Create DNS records:
# A record: api.cosmic-watch.example.com -> <LOAD_BALANCER_IP>
# A record: cosmic-watch.example.com -> <LOAD_BALANCER_IP>
```

## Detailed Deployment

### Architecture

```
┌─────────────────────────────────────────┐
│         Kubernetes Cluster              │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     Ingress (NGINX/ALB)          │  │
│  │  api.cosmic-watch.example.com    │  │
│  │  cosmic-watch.example.com        │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│     ┌─────────┴──────────┐              │
│     │                    │              │
│  ┌──▼────────┐     ┌─────▼───────┐     │
│  │ Backend   │     │  Frontend    │     │
│  │ (3 pods)  │     │  (2 pods)    │     │
│  └────┬──────┘     └──────────────┘     │
│       │                                 │
│  ┌────┴────────┬──────────────┐        │
│  │             │              │         │
│  │      ┌──────▼───┐   ┌─────▼──┐     │
│  │      │ Postgres │   │ Redis  │     │
│  │      │ (StatefulSet) │(1 pod)│     │
│  │      └──────────┘   └────────┘     │
│  │                                     │
│  └─────────────────────────────────────┘
│                                         │
└─────────────────────────────────────────┘
```

### Manifest Files Explanation

#### deployment.yaml
- **Namespace**: Isolates cosmic-watch resources
- **ConfigMap**: Non-sensitive configuration
- **Secret**: Sensitive data (API keys, DB password)
- **PostgreSQL StatefulSet**: Persistent database
- **Redis Deployment**: In-memory cache/sessions
- **Backend Deployment**: 3 replicas with rolling updates
- **Frontend Deployment**: 2 replicas with auto-scaling
- **Services**: Internal networking
- **Ingress**: External access with TLS

#### network-policy.yaml
- **NetworkPolicy**: Restricts pod-to-pod communication
- **ResourceQuota**: Limits namespace resource usage
- **LimitRange**: Sets pod resource constraints

### Scaling

#### Manual Scaling
```bash
# Scale backend to 5 replicas
kubectl scale deployment cosmic-watch-backend --replicas=5 -n cosmic-watch

# Scale frontend to 3 replicas
kubectl scale deployment cosmic-watch-frontend --replicas=3 -n cosmic-watch
```

#### Auto-Scaling (HPA)
Already configured in deployment.yaml:

```bash
# Backend: 2-10 replicas based on 70% CPU, 80% memory
# Frontend: 1-5 replicas based on 75% CPU

# Monitor autoscaler
kubectl get hpa -n cosmic-watch
kubectl describe hpa backend-hpa -n cosmic-watch
```

Install metrics server (required for HPA):
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Database Migrations

```bash
# Access backend pod shell
kubectl exec -it <backend-pod-name> -n cosmic-watch -- /bin/sh

# Run Alembic migrations
alembic upgrade head
```

Or use init containers (add to deployment.yaml):

```yaml
initContainers:
- name: migrations
  image: ghcr.io/yourusername/cosmic-watch-backend:latest
  command: ["python", "-m", "alembic", "upgrade", "head"]
  env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: cosmic-watch-secrets
        key: DATABASE_URL
```

### SSL/TLS Certificates

Using cert-manager (automatic Let's Encrypt):

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.1/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@cosmic-watch.example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Updates and Rollouts

```bash
# Update image tag
kubectl set image deployment/cosmic-watch-backend \
  backend=ghcr.io/yourusername/cosmic-watch-backend:v1.1.0 \
  -n cosmic-watch

# Monitor rollout
kubectl rollout status deployment/cosmic-watch-backend -n cosmic-watch

# Rollback if needed
kubectl rollout undo deployment/cosmic-watch-backend -n cosmic-watch
```

### Backup and Restore

Database backup every 6 hours:

```bash
# Manual backup
kubectl exec postgres-0 -n cosmic-watch -- \
  pg_dump -U cosmicwatch cosmic_watch_db > backup.sql

# Restore from backup
kubectl exec -i postgres-0 -n cosmic-watch -- \
  psql -U cosmicwatch cosmic_watch_db < backup.sql
```

Kubernetes volume snapshot (if using snapshot-controller):

```bash
cat <<EOF | kubectl apply -f -
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: postgres-snapshot
  namespace: cosmic-watch
spec:
  volumeSnapshotClassName: default
  source:
    persistentVolumeClaimName: postgres-storage-postgres-0
EOF
```

### Monitoring (Optional)

#### Prometheus + Grafana

```bash
# Install from Prometheus community Helm chart
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# Create ServiceMonitor for backend
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cosmic-watch-backend
  namespace: cosmic-watch
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: 8000
    path: /metrics
    interval: 30s
EOF
```

#### Loki + Promtail (Logs)

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  -n monitoring \
  --set promtail.enabled=true \
  --set grafana.enabled=true
```

### Troubleshooting

#### Pod won't start
```bash
# Check pod status
kubectl describe pod <pod-name> -n cosmic-watch

# View logs
kubectl logs <pod-name> -n cosmic-watch
kubectl logs <pod-name> -n cosmic-watch --previous  # Previous run

# Check events
kubectl get events -n cosmic-watch --sort-by='.lastTimestamp'
```

#### Database connection failed
```bash
# Test database connectivity from backend pod
kubectl exec <backend-pod> -n cosmic-watch -- \
  python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://cosmicwatch:pwd@postgres:5432/cosmic_watch_db'); print(engine.execute('SELECT 1'))"
```

#### High memory usage
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n cosmic-watch

# Increase memory limit in deployment.yaml
# Then roll out new version
kubectl apply -f k8s/deployment.yaml
```

#### Network connectivity issues
```bash
# Test DNS from pod
kubectl exec <pod-name> -n cosmic-watch -- nslookup postgres

# Check NetworkPolicy
kubectl get networkpolicy -n cosmic-watch
kubectl describe networkpolicy cosmic-watch-network-policy -n cosmic-watch

# Test connectivity between pods
kubectl exec <pod-1> -n cosmic-watch -- wget http://backend:8000/health
```

### Production Checklist

- [ ] Secrets properly configured (strong passwords, API keys)
- [ ] Image pull secrets configured if using private registry
- [ ] Resource requests/limits set appropriately
- [ ] HPA configured and metrics-server running
- [ ] Ingress configured with TLS cert-manager
- [ ] Database backups automated (CronJob)
- [ ] Pod disruption budgets created
- [ ] Network policies thoroughly tested
- [ ] Monitoring & logging deployed (Prometheus, Loki)
- [ ] Alerting configured
- [ ] Load testing completed
- [ ] Disaster recovery plan documented
- [ ] Secrets rotated regularly
- [ ] RBAC policies implemented

### Cloud-Specific Configuration

#### AWS EKS

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Create PersistentVolume using EBS
cat <<EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
EOF
```

#### Google Kubernetes Engine (GKE)

```bash
# Configure kubectl
gcloud container clusters get-credentials my-cluster --zone us-central1-a

# Use Workload Identity for pod auth
kubectl annotate serviceaccount cosmic-watch-backend \
  iam.gke.io/gcp-service-account=cosmic-watch-backend@my-project.iam.gserviceaccount.com \
  -n cosmic-watch
```

#### Azure Kubernetes Service (AKS)

```bash
# Get credentials
az aks get-credentials --resource-group myResourceGroup --name myAksCluster

# Use Azure identity
kubectl create namespace cosmic-watch
helm repo add aad-pod-identity https://raw.githubusercontent.com/Azure/aad-pod-identity/master/charts
```

## Maintenance

### Daily
- Monitor dashboard (Grafana/Prometheus)
- Check pod status and logs
- Verify no pending PVCs

### Weekly
- Review resource usage trends
- Check for security updates
- Test backup/restore procedures

### Monthly
- Certificate renewal (automatic with cert-manager)
- Update base images
- Review and update network policies
- Capacity planning review

## Support & Documentation

- Kubernetes docs: https://kubernetes.io/docs
- Kubectl cheatsheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Troubleshooting: https://kubernetes.io/docs/tasks/debug-application-cluster/

