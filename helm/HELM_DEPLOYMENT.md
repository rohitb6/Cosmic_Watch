# Helm Deployment Quick Start

Complete guide to deploy Cosmic Watch using Helm to any Kubernetes cluster.

## Prerequisites

```bash
# Check Kubernetes cluster connectivity
kubectl cluster-info
kubectl get nodes

# Check Helm version (3.x required)
helm version

# Check ingress controller installed (for NGINX)
kubectl get ingressclass
```

## Step 1: Add Bitnami Helm Repository

For PostgreSQL and Redis dependencies:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

## Step 2: Create Secrets File

Create `secrets.yaml` with your actual values:

```yaml
global:
  environment: production
  domain: cosmic-watch.example.com

namespace:
  create: true
  name: cosmic-watch

# Database password - use strong password
postgresql:
  enabled: true
  auth:
    password: "generate-strong-password-here"

backend:
  secrets:
    DATABASE_URL: "postgresql://cosmicwatch:generate-strong-password-here@postgres:5432/cosmic_watch_db"
    REDIS_URL: "redis://redis:6379/0"
    SECRET_KEY: "generate-another-strong-secret-key"
    NASA_API_KEY: "your-actual-nasa-api-key-from-api.nasa.gov"
    OPENAI_API_KEY: "your-actual-openai-api-key-from-platform.openai.com"

frontend:
  env:
    VITE_API_URL: "https://api.cosmic-watch.example.com"

ingress:
  hosts:
    - host: api.cosmic-watch.example.com
      paths:
        - path: /
          pathType: Prefix
          service: backend
          port: 8000
    - host: cosmic-watch.example.com
      paths:
        - path: /
          pathType: Prefix
          service: frontend
          port: 3000
```

**Generate secure passwords:**
```bash
# Generate secure password
openssl rand -base64 32
# Generate secure secret key
openssl rand -hex 32
```

## Step 3: Update Image References

Edit `helm/values.yaml` and update image repositories:

```yaml
backend:
  image:
    registry: ghcr.io
    repository: your-username/cosmic-watch-backend
    tag: latest

frontend:
  image:
    registry: ghcr.io
    repository: your-username/cosmic-watch-frontend
    tag: latest
```

Or override during installation:

```bash
helm install cosmic-watch ./helm \
  -f secrets.yaml \
  --set backend.image.repository=your-username/cosmic-watch-backend \
  --set frontend.image.repository=your-username/cosmic-watch-frontend \
  --namespace cosmic-watch \
  --create-namespace
```

## Step 4: Validate Helm Chart

```bash
# Check chart syntax
helm lint ./helm

# Validate generated manifests
helm template cosmic-watch ./helm -f secrets.yaml | kubectl apply --dry-run=client -f -

# Preview all objects that will be created
helm template cosmic-watch ./helm -f secrets.yaml
```

## Step 5: Install

```bash
helm install cosmic-watch ./helm \
  -f secrets.yaml \
  --namespace cosmic-watch \
  --create-namespace
```

Verify installation:
```bash
helm list -n cosmic-watch
helm status cosmic-watch -n cosmic-watch
```

## Step 6: Wait for Pods to be Ready

```bash
# Watch pod startup
kubectl get pods -n cosmic-watch -w

# Check specific pod
kubectl describe pod <pod-name> -n cosmic-watch

# View logs
kubectl logs <pod-name> -n cosmic-watch
```

## Step 7: Configure DNS

Get the Ingress IP:
```bash
kubectl get ingress -n cosmic-watch
```

Point your DNS A records:
```
api.cosmic-watch.example.com  -> <INGRESS_IP>
cosmic-watch.example.com      -> <INGRESS_IP>
```

Or using DNS provider CLI:
```bash
# AWS Route53
aws route53 change-resource-record-sets \
  --hosted-zone-id Z... \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.cosmic-watch.example.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "YOUR_IP"}]
      }
    }]
  }'
```

## Step 8: Verify Deployment

```bash
# Check all resources
kubectl get all -n cosmic-watch

# Test backend health
kubectl port-forward -n cosmic-watch svc/backend 8000:8000
curl http://localhost:8000/health

# Test frontend
kubectl port-forward -n cosmic-watch svc/frontend 3000:3000
# Visit http://localhost:3000 in browser
```

## Common Helm Commands

### View Release Info
```bash
helm show values ./helm
helm show chart ./helm
helm show all ./helm
```

### Upgrade Release
```bash
helm upgrade cosmic-watch ./helm \
  -f secrets.yaml \
  --namespace cosmic-watch
```

### Check What Changed
```bash
helm diff upgrade cosmic-watch ./helm \
  -f secrets.yaml \
  --namespace cosmic-watch
```

### Rollback
```bash
helm rollback cosmic-watch -n cosmic-watch
helm rollback cosmic-watch 1 -n cosmic-watch  # to specific revision
```

### View History
```bash
helm history cosmic-watch -n cosmic-watch
```

### Uninstall
```bash
helm uninstall cosmic-watch -n cosmic-watch
```

## Customization Examples

### Development Deployment
```yaml
# dev-values.yaml
backend:
  replicaCount: 1
  resources:
    limits:
      memory: "512Mi"

frontend:
  replicaCount: 1
  resources:
    limits:
      memory: "256Mi"

postgresql:
  primary:
    persistence:
      size: 5Gi

redis:
  master:
    persistence:
      size: 1Gi
```

Install:
```bash
helm install cosmic-watch-dev ./helm \
  -f secrets.yaml \
  -f dev-values.yaml \
  --namespace cosmic-watch-dev \
  --create-namespace
```

### Production Deployment
```yaml
# prod-values.yaml
backend:
  replicaCount: 5
  autoscaling:
    minReplicas: 3
    maxReplicas: 20
  resources:
    limits:
      memory: "2Gi"
      cpu: "2000m"

frontend:
  replicaCount: 3
  autoscaling:
    minReplicas: 2
    maxReplicas: 10

postgresql:
  primary:
    persistence:
      size: 50Gi
  metrics:
    enabled: true

redis:
  master:
    persistence:
      size: 10Gi
  replica:
    replicaCount: 2

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

Install:
```bash
helm install cosmic-watch ./helm \
  -f secrets.yaml \
  -f prod-values.yaml \
  --namespace cosmic-watch-prod \
  --create-namespace
```

## Database Management

### Run Migrations
```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pod -n cosmic-watch -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -it $BACKEND_POD -n cosmic-watch -- \
  python -m alembic upgrade head
```

### Backup Database
```bash
POSTGRES_POD=$(kubectl get pod -n cosmic-watch -l app=postgres -o jsonpath='{.items[0].metadata.name}')

kubectl exec $POSTGRES_POD -n cosmic-watch -- \
  pg_dump -U cosmicwatch cosmic_watch_db > backup-$(date +%Y%m%d-%H%M%S).sql
```

### Restore Database
```bash
POSTGRES_POD=$(kubectl get pod -n cosmic-watch -l app=postgres -o jsonpath='{.items[0].metadata.name}')

kubectl exec -i $POSTGRES_POD -n cosmic-watch -- \
  psql -U cosmicwatch cosmic_watch_db < backup.sql
```

## Scaling

### Manual Scale
```bash
# Scale backend to 10 replicas
kubectl scale deployment cosmic-watch-backend --replicas=10 -n cosmic-watch

# Scale frontend to 5 replicas
kubectl scale deployment cosmic-watch-frontend --replicas=5 -n cosmic-watch
```

### Auto-Scaling
Already configured via HPA:
```bash
# View current HPA
kubectl get hpa -n cosmic-watch

# Watch HPA activity
kubectl get hpa -n cosmic-watch -w
```

## Monitoring

### View Logs
```bash
# Backend logs
kubectl logs -f deployment/cosmic-watch-backend -n cosmic-watch

# Frontend logs
kubectl logs -f deployment/cosmic-watch-frontend -n cosmic-watch

# Postgres logs
kubectl logs -f statefulset/postgres -n cosmic-watch
```

### Port Forwarding
```bash
# Access backend directly
kubectl port-forward -n cosmic-watch svc/backend 8000:8000

# Access frontend directly
kubectl port-forward -n cosmic-watch svc/frontend 3000:3000

# Access database
kubectl port-forward -n cosmic-watch svc/postgres 5432:5432
```

## Troubleshooting

### Pod keeps crashing
```bash
# Check pod events
kubectl describe pod <pod-name> -n cosmic-watch

# Check previous logs
kubectl logs <pod-name> -n cosmic-watch --previous

# Get more context
kubectl get events -n cosmic-watch --sort-by='.lastTimestamp'
```

### Database connection failed
```bash
# Verify database service is running
kubectl get svc postgres -n cosmic-watch

# Check PostgreSQL logs
kubectl logs statefulset/postgres -n cosmic-watch

# Test connection from backend pod
kubectl exec <backend-pod> -n cosmic-watch -- \
  python -c "import os; from sqlalchemy import create_engine; \
  engine = create_engine(os.environ['DATABASE_URL']); \
  print(engine.execute('SELECT 1'))"
```

### Ingress not working
```bash
# Check ingress
kubectl get ingress -n cosmic-watch
kubectl describe ingress cosmic-watch -n cosmic-watch

# Check ingress controller
kubectl get pods -n ingress-nginx

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup cosmic-watch.example.com
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Deploy with Helm
  run: |
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
    helm upgrade --install cosmic-watch ./helm \
      --namespace cosmic-watch \
      --create-namespace \
      --values secrets.yaml \
      --set backend.image.tag=${{ github.sha }}
```

### GitOps (ArgoCD)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cosmic-watch
spec:
  project: default
  source:
    repoURL: https://github.com/yourusername/cosmic-watch
    targetRevision: main
    path: helm
    helm:
      valueFiles:
      - secrets.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: cosmic-watch
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Additional Resources

- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Bitnami Helm Charts](https://github.com/bitnami/charts)
- [Chart Best Practices](https://helm.sh/docs/chart_best_practices/)
