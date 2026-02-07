# Cosmic Watch Helm Chart

A production-ready Helm 3 chart for deploying Cosmic Watch to Kubernetes clusters.

## Quick Start

### Prerequisites
- Kubernetes 1.24+ cluster
- Helm 3.x
- Container images pushed to a registry

### Installation

1. **Create secrets file** (`secrets.yaml`):
```yaml
backend:
  secrets:
    DATABASE_URL: "postgresql://cosmicwatch:YOUR_PASSWORD@postgres:5432/cosmic_watch_db"
    REDIS_URL: "redis://redis:6379/0"
    SECRET_KEY: "your-secure-random-key"
    NASA_API_KEY: "your-nasa-api-key"
    OPENAI_API_KEY: "your-openai-api-key"
```

2. **Update image repositories** in `values.yaml`:
```yaml
backend:
  image:
    repository: yourusername/cosmic-watch-backend

frontend:
  image:
    repository: yourusername/cosmic-watch-frontend
```

3. **Install the chart**:
```bash
helm install cosmic-watch ./helm \
  -f secrets.yaml \
  --namespace cosmic-watch \
  --create-namespace
```

4. **Verify installation**:
```bash
kubectl get all -n cosmic-watch
kubectl get ingress -n cosmic-watch
```

## Chart Structure

```
helm/
├── Chart.yaml                 # Chart metadata
├── values.yaml               # Default values
├── charts/                   # Dependencies (postgresql, redis)
└── templates/
    ├── _helpers.tpl         # ConfigMap, Secrets, RBAC
    ├── backend.yaml         # Backend deployment & service
    ├── frontend.yaml        # Frontend deployment & service
    ├── ingress.yaml         # Ingress configuration
    └── network-policy.yaml  # Network policies & quotas
```

## Configuration

### Key Values

#### Backend
```yaml
backend:
  replicaCount: 3
  image:
    tag: latest
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
```

#### Frontend
```yaml
frontend:
  replicaCount: 2
  image:
    tag: latest
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
```

#### Ingress
```yaml
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.cosmic-watch.example.com
      paths:
        - path: /
          service: backend
          port: 8000
```

#### PostgreSQL (via Bitnami subchart)
```yaml
postgresql:
  enabled: true
  auth:
    username: cosmicwatch
    password: changeme
    database: cosmic_watch_db
  primary:
    persistence:
      size: 10Gi
```

#### Redis (via Bitnami subchart)
```yaml
redis:
  enabled: true
  master:
    persistence:
      size: 2Gi
```

### Advanced Configuration

#### Custom Secrets
```bash
# Use existing secret instead of creating new one
kubectl create secret generic cosmic-watch-secrets \
  --from-literal=DATABASE_URL='...' \
  --from-literal=REDIS_URL='...' \
  -n cosmic-watch
```

#### Private Container Registry
```bash
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token> \
  -n cosmic-watch
```

Add to values.yaml:
```yaml
imagePullSecrets:
  - name: regcred
```

#### Enable Monitoring
```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

#### Enable Backup
```yaml
backup:
  enabled: true
  schedule: "0 2 * * *"    # Daily at 2 AM UTC
  retention: 30             # Keep 30 days backups
```

## Deployment with Custom Values

### Development Environment
```bash
helm install cosmic-watch ./helm \
  --namespace cosmic-watch-dev \
  --set backend.replicaCount=1 \
  --set frontend.replicaCount=1 \
  --set postgresql.primary.persistence.size=5Gi \
  -f dev-secrets.yaml
```

### Production Environment
```bash
helm install cosmic-watch ./helm \
  --namespace cosmic-watch-prod \
  -f prod-secrets.yaml \
  -f prod-values.yaml
```

### Staging Environment
```bash
helm install cosmic-watch ./helm \
  --namespace cosmic-watch-staging \
  -f staging-secrets.yaml \
  -f staging-values.yaml
```

## Upgrade Management

### Check for Changes
```bash
helm diff upgrade cosmic-watch ./helm \
  -f secrets.yaml
```

### Perform Upgrade
```bash
helm upgrade cosmic-watch ./helm \
  -f secrets.yaml \
  --namespace cosmic-watch
```

### Rollback to Previous Release
```bash
helm rollback cosmic-watch -n cosmic-watch
```

### View Release History
```bash
helm history cosmic-watch -n cosmic-watch
```

## Database Operations

### Run Migrations
```bash
# Using kubectl exec
kubectl exec -it cosmic-watch-backend-xxx -n cosmic-watch -- \
  python -m alembic upgrade head
```

### Backup Database
```bash
kubectl exec postgres-0 -n cosmic-watch -- \
  pg_dump -U cosmicwatch cosmic_watch_db > backup.sql
```

### Restore Database
```bash
kubectl exec -i postgres-0 -n cosmic-watch -- \
  psql -U cosmicwatch cosmic_watch_db < backup.sql
```

## Troubleshooting

### Check Helm Chart Syntax
```bash
helm lint ./helm
```

### Dry Run Installation
```bash
helm install cosmic-watch ./helm \
  --namespace cosmic-watch \
  --create-namespace \
  --dry-run \
  --debug
```

### View Generated Manifests
```bash
helm template cosmic-watch ./helm \
  -f secrets.yaml
```

### Check Pod Status
```bash
kubectl describe pod <pod-name> -n cosmic-watch
kubectl logs <pod-name> -n cosmic-watch
```

### Debugging Deployments
```bash
# Check deployment status
kubectl rollout status deployment/cosmic-watch-backend -n cosmic-watch

# View recent events
kubectl get events -n cosmic-watch --sort-by='.lastTimestamp'

# Enter pod shell
kubectl exec -it <pod-name> -n cosmic-watch -- /bin/sh
```

## Security Best Practices

1. **Never commit secrets** to version control:
   ```bash
   # Use secrets in separate file
   helm install cosmic-watch ./helm -f secrets.yaml
   
   # Or use Google Cloud Secret Manager
   gcloud secrets create cosmic-watch-secrets --data-file=secrets.yaml
   ```

2. **Use strong passwords**:
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

3. **Enable NetworkPolicies**:
   ```yaml
   networkPolicy:
     enabled: true
     ingress:
       enabled: true
     egress:
       enabled: true
   ```

4. **Set resource limits**:
   ```yaml
   resources:
     requests:
       memory: "512Mi"
       cpu: "250m"
     limits:
       memory: "1Gi"
       cpu: "1000m"
   ```

5. **Use RBAC**:
   ```yaml
   rbac:
     create: true
   ```

6. **Enable TLS**:
   ```yaml
   ingress:
     tls:
       enabled: true
       issuer: letsencrypt-prod
   ```

## Multiple Environment Management

Create separate values files:

**prod-values.yaml:**
```yaml
backend:
  replicaCount: 5
  resources:
    limits:
      memory: "2Gi"
      cpu: "2000m"
  autoscaling:
    maxReplicas: 20

ingress:
  hosts:
    - host: api.cosmic-watch.com
```

**staging-values.yaml:**
```yaml
backend:
  replicaCount: 2
  resources:
    limits:
      memory: "1Gi"
      cpu: "1000m"

ingress:
  hosts:
    - host: api-staging.cosmic-watch.com
```

Deploy with:
```bash
helm install cosmic-watch-prod ./helm \
  -f prod-secrets.yaml \
  -f prod-values.yaml \
  -n cosmic-watch-prod

helm install cosmic-watch-staging ./helm \
  -f staging-secrets.yaml \
  -f staging-values.yaml \
  -n cosmic-watch-staging
```

## Monitoring Integration

### Prometheus
```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
```

### Grafana Dashboards
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

## Support

For issues and documentation:
- GitHub: https://github.com/yourusername/cosmic-watch
- Documentation: See `/docs/KUBERNETES_DEPLOYMENT.md`
