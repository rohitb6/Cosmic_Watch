# Docker Deployment Guide - Cosmic Watch

Complete guide for deploying Cosmic Watch using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

## Quick Start - Development

### 1. Clone and Configure

```bash
cd cosmic-watch
cp .env.example .env
```

### 2. Update Environment Variables

Edit `.env` with your configuration:

```env
# Database
DB_PASSWORD=your-secure-password

# API Keys
NASA_API_KEY=your-nasa-api-key
OPENAI_API_KEY=your-openai-key

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# Debug Mode
DEBUG=True

# Frontend API
VITE_API_URL=http://localhost:8000
```

### 3. Start All Services

```bash
# Start in background
docker-compose up -d

# Or with logs
docker-compose up

# Check status
docker-compose ps
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Database**: localhost:5432

### 5. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## Production Deployment

### 1. Environment Setup

Create a production `.env`:

```env
DB_PASSWORD=generate-strong-password
SECRET_KEY=generate-secure-key-256-bits
NASA_API_KEY=your-real-nasa-key
OPENAI_API_KEY=your-real-openai-key
DEBUG=False
VITE_API_URL=https://api.yourdomain.com
```

### 2. Production Docker Compose

```bash
# Start with production profile (includes Nginx)
docker-compose --profile production up -d
```

### 3. SSL/TLS Setup

Create `ssl/` directory with certificates:

```bash
mkdir -p ssl
# Copy your cert.pem and key.pem here
cp /path/to/cert.pem ssl/
cp /path/to/key.pem ssl/
```

### 4. Nginx Configuration

Update `nginx.conf`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Building Custom Images

### Build All Images

```bash
# Development
docker-compose build

# Production (no cache)
docker-compose build --no-cache
```

### Build Specific Service

```bash
docker-compose build backend
docker-compose build frontend
```

## Database Management

### Access PostgreSQL

```bash
# Connect to database
docker-compose exec postgres psql -U cosmicwatch -d cosmic_watch_db

# Backup database
docker-compose exec postgres pg_dump -U cosmicwatch cosmic_watch_db > backup.sql

# Restore database
docker cp backup.sql cosmic-watch-db:/tmp/
docker-compose exec postgres psql -U cosmicwatch -d cosmic_watch_db < /tmp/backup.sql
```

### Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

## Cache Management

### Access Redis

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:3000
```

### View Resource Usage

```bash
docker stats cosmic-watch-backend cosmic-watch-frontend cosmic-watch-db
```

### Clean Up

```bash
# Stop services
docker-compose down

# Remove volumes (erase data)
docker-compose down -v

# Remove all unused resources
docker system prune -a
```

## Troubleshooting

### Backend won't connect to database

```bash
# Check database is healthy
docker-compose logs postgres

# Verify connection
docker-compose exec backend python -c "from app.core.database import SessionLocal; SessionLocal()"
```

### Frontend can't reach API

```bash
# Check VITE_API_URL is correct
docker-compose logs frontend

# Verify backend is accessible
docker-compose exec frontend curl http://backend:8000/health
```

### Port already in use

```bash
# Change ports in docker-compose.yml
# Or stop conflicting service
lsof -i :8000  # Find process on port 8000
```

## Cloud Deployment

### AWS ECS

1. Create ECR repositories
2. Build and push images:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag cosmic-watch-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/cosmic-watch-backend:latest
```

3. Create ECS task definitions
4. Deploy services

### Google Cloud Run

```bash
# Enable required APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Build and deploy backend
gcloud run deploy cosmic-watch-backend \
  --source backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --env-vars-file .env
```

### Heroku

```bash
# Create app
heroku create cosmic-watch

# Set environment variables
heroku config:set NASA_API_KEY=your-key
heroku config:set OPENAI_API_KEY=your-key

# Deploy
git push heroku main
```

## Scaling

### Horizontal Scaling

```bash
# Run multiple backend instances
docker-compose up -d --scale backend=3

# Use Nginx for load balancing
```

### Resource Limits

Update docker-compose.yml:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Security Best Practices

1. **Never commit .env** - Use `.env.example` template
2. **Rotate secrets** - Change SECRET_KEY and DB_PASSWORD regularly
3. **Use strong passwords** - Min 20 characters for production
4. **Enable SSL/TLS** - Always use HTTPS in production
5. **Network isolation** - Keep services on private network
6. **Auth tokens** - Implement token rotation
7. **Regular updates** - Keep images updated

## Performance Optimization

```bash
# Enable Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker-compose build

# Multi-stage builds already reduce image size
# Frontend: 150MB → 50MB
# Backend: 300MB → 200MB
```

## Monitoring Stack (Optional)

```yaml
# Add to docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
```

## Support

For issues, check:
- `docker-compose logs <service>` for error messages
- Health endpoints at `/health`
- API documentation at `/api/docs`
- See [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
