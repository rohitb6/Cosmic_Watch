# Deployment Commands Quick Reference

## Docker Compose

### Development
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Restart specific service
docker-compose restart backend

# Rebuild images
docker-compose build --no-cache
```

### Production
```bash
# Start with production profile
docker-compose --profile production up -d

# Check health
docker-compose ps

# Cleanup old images
docker image prune -a
```

---

## Kubernetes (raw manifests)

### Deploy
```bash
# Create namespace
kubectl create namespace cosmic-watch

# Apply all manifests
kubectl apply -f k8s/

# Verify deployment
kubectl get all -n cosmic-watch
```

### Monitor
```bash
# Watch pods
kubectl get pods -n cosmic-watch -w

# View logs
kubectl logs -f deployment/cosmic-watch-backend -n cosmic-watch

# Describe pod
kubectl describe pod <pod-name> -n cosmic-watch

# Get events
kubectl get events -n cosmic-watch --sort-by='.lastTimestamp'
```

### Scale
```bash
# Manual scale
kubectl scale deployment cosmic-watch-backend --replicas=5 -n cosmic-watch

# View HPA status
kubectl get hpa -n cosmic-watch
```

### Database
```bash
# Run migrations
kubectl exec <backend-pod> -n cosmic-watch -- python -m alembic upgrade head

# Backup database
kubectl exec postgres-0 -n cosmic-watch -- \
  pg_dump -U cosmicwatch cosmic_watch_db > backup.sql

# Enter database shell
kubectl exec -it postgres-0 -n cosmic-watch -- \
  psql -U cosmicwatch -d cosmic_watch_db
```

### Cleanup
```bash
# Delete all resources
kubectl delete namespace cosmic-watch

# Delete specific resource
kubectl delete deployment cosmic-watch-backend -n cosmic-watch
```

---

## Helm

### Install
```bash
# Add dependencies
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Validate chart
helm lint ./helm
helm template cosmic-watch ./helm -f secrets.yaml

# Install
helm install cosmic-watch ./helm -f secrets.yaml -n cosmic-watch --create-namespace

# Check status
helm status cosmic-watch -n cosmic-watch
```

### Update
```bash
# Check what will change
helm diff upgrade cosmic-watch ./helm -f secrets.yaml -n cosmic-watch

# Upgrade
helm upgrade cosmic-watch ./helm -f secrets.yaml -n cosmic-watch

# Monitor rollout
kubectl rollout status deployment/cosmic-watch-backend -n cosmic-watch -w
```

### Rollback
```bash
# View history
helm history cosmic-watch -n cosmic-watch

# Rollback to previous release
helm rollback cosmic-watch -n cosmic-watch

# Rollback to specific revision
helm rollback cosmic-watch 3 -n cosmic-watch
```

### Uninstall
```bash
# Uninstall
helm uninstall cosmic-watch -n cosmic-watch

# Delete namespace
kubectl delete namespace cosmic-watch
```

### Customize
```bash
# Override values during install
helm install cosmic-watch ./helm \
  -f secrets.yaml \
  --set backend.replicaCount=5 \
  --set frontend.image.tag=v1.0.0 \
  -n cosmic-watch --create-namespace

# Use multiple values files
helm install cosmic-watch ./helm \
  -f secrets.yaml \
  -f prod-values.yaml \
  -n cosmic-watch-prod
```

---

## Docker Images

### Build
```bash
# Build backend
docker build -t your-org/cosmic-watch-backend:latest ./backend

# Build frontend
docker build -t your-org/cosmic-watch-frontend:latest ./frontend

# Build with specific tag
docker build -t your-org/cosmic-watch-backend:v1.0.0 ./backend
```

### Push
```bash
# Login to registry
docker login ghcr.io
# or: aws ecr get-login-password | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Push images
docker push your-org/cosmic-watch-backend:latest
docker push your-org/cosmic-watch-frontend:latest

# Push with tag
docker push your-org/cosmic-watch-backend:v1.0.0
```

### List & Clean
```bash
# List images
docker images | grep cosmic-watch

# Remove image
docker rmi your-org/cosmic-watch-backend:latest

# Cleanup unused
docker image prune -a
```

---

## Kubernetes Port Forwarding

### Access Services
```bash
# Backend API
kubectl port-forward -n cosmic-watch svc/backend 8000:8000
# Access: http://localhost:8000

# Frontend
kubectl port-forward -n cosmic-watch svc/frontend 3000:3000
# Access: http://localhost:3000

# Database
kubectl port-forward -n cosmic-watch svc/postgres 5432:5432

# Redis
kubectl port-forward -n cosmic-watch svc/redis 6379:6379
```

---

## Debugging

### Pod Issues
```bash
# Get pod status
kubectl get pod <pod-name> -n cosmic-watch -o wide

# Describe pod (check events/status)
kubectl describe pod <pod-name> -n cosmic-watch

# View logs
kubectl logs <pod-name> -n cosmic-watch

# View previous logs (if crashed)
kubectl logs <pod-name> -n cosmic-watch --previous

# Enter pod shell
kubectl exec -it <pod-name> -n cosmic-watch -- /bin/sh

# Run command in pod
kubectl exec <pod-name> -n cosmic-watch -- python --version
```

### Deployment Issues
```bash
# Check deployment status
kubectl rollout status deployment/cosmic-watch-backend -n cosmic-watch

# View rollout history
kubectl rollout history deployment/cosmic-watch-backend -n cosmic-watch

# Rollback deployment
kubectl rollout undo deployment/cosmic-watch-backend -n cosmic-watch

# Watch pod events during deployment
kubectl get events -n cosmic-watch -w
```

### Network Connectivity
```bash
# Test DNS from pod
kubectl exec <pod-name> -n cosmic-watch -- nslookup backend

# Test connection between pods
kubectl exec <pod-name> -n cosmic-watch -- wget http://backend:8000/health

# Check service endpoints
kubectl get endpoints -n cosmic-watch

# Describe service
kubectl describe svc backend -n cosmic-watch
```

---

## Production Operations

### Daily Checks
```bash
# Pod status
kubectl get pods -n cosmic-watch

# Resource usage
kubectl top nodes
kubectl top pods -n cosmic-watch

# Check for warnings/errors
kubectl get events -n cosmic-watch | grep -E "Warning|Error"
```

### Weekly Tasks
```bash
# Test backup
kubectl exec postgres-0 -n cosmic-watch -- \
  pg_dump -U cosmicwatch cosmic_watch_db | head -c 1000

# Check certificate expiration (if using cert-manager)
kubectl get certificate -n cosmic-watch
```

### Monthly Tasks
```bash
# Update images
docker pull your-org/cosmic-watch-backend
docker tag your-org/cosmic-watch-backend:latest your-org/cosmic-watch-backend:v1.1.0
docker push your-org/cosmic-watch-backend:v1.1.0

# Upgrade Helm chart
helm repo update
helm upgrade cosmic-watch ./helm -n cosmic-watch

# Review and rotate secrets
kubectl create secret generic cosmic-watch-secrets --from-literal=... --dry-run=client -o yaml | kubectl apply -f -
```

---

## CI/CD

### GitHub Actions
```bash
# View workflow runs
gh run list -R yourusername/cosmic-watch

# View specific workflow
gh run view <run-id> -R yourusername/cosmic-watch

# Trigger workflow manually
gh workflow run deploy.yml -R yourusername/cosmic-watch

# View logs of recent run
gh run view -R yourusername/cosmic-watch --log
```

### Manual Docker Build & Push
```bash
# Build backend
docker build -t ghcr.io/yourusername/cosmic-watch-backend:v1.0.0 ./backend

# Build frontend
docker build -t ghcr.io/yourusername/cosmic-watch-frontend:v1.0.0 ./frontend

# Login to GitHub Container Registry
echo $GH_TOKEN | docker login ghcr.io -u yourusername --password-stdin

# Push images
docker push ghcr.io/yourusername/cosmic-watch-backend:v1.0.0
docker push ghcr.io/yourusername/cosmic-watch-frontend:v1.0.0

# Deploy
helm upgrade cosmic-watch ./helm \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0 \
  -n cosmic-watch
```

---

## Environment Setup

### Prerequisites Installation
```bash
# macOS
brew install docker docker-compose kubectl helm

# Ubuntu/Debian
sudo apt-get install docker.io docker-compose kubectl

# Windows (WSL2)
wsl --install ubuntu-20.04
sudo apt-get install docker.io docker-compose kubectl
```

### Configure kubectl
```bash
# AWS EKS
aws eks update-kubeconfig --name my-cluster --region us-east-1

# Google GKE
gcloud container clusters get-credentials my-cluster --zone us-central1-a

# Azure AKS
az aks get-credentials --resource-group myResourceGroup --name myAksCluster

# Local cluster (Minikube/Kind)
kubectl cluster-info
```

### Verify Installation
```bash
docker --version
docker-compose --version
kubectl version --client
helm version
```

---

## Useful Aliases (add to .bashrc/.zshrc)

```bash
alias kgp='kubectl get pods -n cosmic-watch'
alias kgs='kubectl get svc -n cosmic-watch'
alias kd='kubectl describe'
alias kdf='kubectl delete'
alias kdp='kubectl describe pod'
alias kl='kubectl logs -f'
alias ke='kubectl exec -it'
alias kgd='kubectl get deployment -n cosmic-watch'
alias kgn='kubectl get nodes'
alias kgh='helm list -n cosmic-watch'
```

---

## Troubleshooting Quick Links

**Docker won't start:**
```bash
docker system prune -a
docker-compose rebuild
```

**Pod stuck in Pending:**
```bash
kubectl describe node  # Check node capacity
kubectl describe pod   # Check pod requests vs available
```

**Connection refused errors:**
```bash
kubectl get svc -n cosmic-watch  # Verify services exist
kubectl exec pod -- nslookup backend  # Check DNS
```

**Image pull errors:**
```bash
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token> \
  -n cosmic-watch
```

**Database connection failed:**
```bash
kubectl exec pod -- \
  psql -h postgres -U cosmicwatch -d cosmic_watch_db
```

---

## Common Patterns

### Deploy new version
```bash
# 1. Build & push image
docker build -t your-org/backend:v1.1.0 ./backend
docker push your-org/backend:v1.1.0

# 2. Update deployment
kubectl set image deployment/cosmic-watch-backend \
  backend=your-org/backend:v1.1.0 \
  -n cosmic-watch

# 3. Monitor rollout
kubectl rollout status deployment/cosmic-watch-backend -n cosmic-watch -w
```

### Scale & test
```bash
# 1. Increase replicas
kubectl scale deployment cosmic-watch-backend --replicas=5 -n cosmic-watch

# 2. Monitor metrics
kubectl top pods -n cosmic-watch -w

# 3. Scale down
kubectl scale deployment cosmic-watch-backend --replicas=3 -n cosmic-watch
```

### Quick restore
```bash
# 1. Backup current state
kubectl get all -n cosmic-watch -o yaml > backup.yaml

# 2. Restore from file
kubectl apply -f backup.yaml

# 3. Or rollback from Kubernetes
kubectl rollout undo deployment/cosmic-watch-backend -n cosmic-watch
```

