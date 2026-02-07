# Environment Configuration Guide

## Production Environment Variables

Copy this to your `.env` file and configure for your environment.

### 🔐 Security Configuration

```bash
# SECRET_KEY: Used for JWT token signing
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-secret-key-here-generate-with-python

# JWT Settings
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
JWT_REFRESH_EXPIRATION_DAYS=7
PASSWORD_MIN_LENGTH=8

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://cosmic-watch.io
ALLOWED_HOSTS=localhost,127.0.0.1,cosmic-watch.io
```

### 🌍 API Configuration

```bash
# NASA API
NASA_API_KEY=your-nasa-api-key-from-https-api-nasa-gov
NASA_API_BASE_URL=https://api.nasa.gov/neo/rest/v1
NASA_API_TIMEOUT=30

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=5000
```

### 🗄️ Database Configuration

```bash
# PostgreSQL
DATABASE_URL=postgresql://cosmicwatch:password@postgres:5432/cosmic_watch_db
DB_ECHO=False  # Set True to see SQL queries in logs
DB_POOL_SIZE=10
DB_POOL_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600  # Recycle connections every hour

# For local development
# DATABASE_URL=postgresql://cosmicwatch:local_password@localhost:5432/cosmic_watch_db
```

### 💾 Redis Configuration

```bash
# Redis
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL_ASTEROIDS=21600  # 6 hours
REDIS_CACHE_TTL_APPROACHES=10800  # 3 hours
REDIS_CACHE_TTL_SEARCH=3600      # 1 hour
```

### 📱 Frontend Configuration

```bash
# These are served to the frontend via environment variables
REACT_APP_API_URL=http://localhost:8000
REACT_APP_TIMEOUT=30000  # milliseconds
REACT_APP_ENV=development

# For production
# REACT_APP_API_URL=https://api.cosmic-watch.io
# REACT_APP_ENV=production
```

### 📧 Email Configuration (Optional)

```bash
# SMTP Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Email Templates
EMAIL_FROM_NAME=Cosmic Watch
EMAIL_FROM_ADDRESS=noreply@cosmic-watch.io
ALERT_EMAIL_ENABLED=True
```

### 📊 Logging Configuration

```bash
# Logging Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
LOG_FILE=/app/logs/cosmic-watch.log
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# For development
# LOG_LEVEL=DEBUG
```

### 🚀 Deployment Configuration

```bash
# Application Environment
DEBUG=False  # NEVER set to True in production
ENVIRONMENT=production
APP_NAME=Cosmic Watch
APP_VERSION=1.0.0

# For development
# DEBUG=True
# ENVIRONMENT=development
```

### 🔄 Background Job Configuration

```bash
# APScheduler Settings
SCHEDULER_ENABLED=True
SCHEDULER_TIMEZONE=UTC

# NASA API Sync Job (every 6 hours)
NASA_SYNC_INTERVAL_HOURS=6

# Alert Check Job (every 30 minutes)
ALERT_CHECK_INTERVAL_MINUTES=30
```

### 📈 Monitoring Configuration

```bash
# Health Check Endpoints
HEALTH_CHECK_ENABLED=True
METRICS_ENABLED=True

# Sentry Error Tracking (Optional)
SENTRY_DSN=""  # Leave empty to disable

# Custom Monitoring
TRACK_API_METRICS=True
```

---

## 🔧 How to Set Up

### Docker Compose Environment

1. **Copy template:**
   ```bash
   cp .env.example .env
   ```

2. **Get NASA API Key:**
   - Visit https://api.nasa.gov
   - Register for free
   - Copy your API key

3. **Generate SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Update .env:**
   ```bash
   nano .env  # or use your favorite editor
   ```

5. **Start services:**
   ```bash
   docker-compose up -d
   ```

---

## 🏠 Local Development Setup

### Backend

```bash
cd backend

# Create .env.local
cat > .env.local << EOF
SECRET_KEY=dev-key-12345678901234567890123456789012
DATABASE_URL=postgresql://cosmicwatch:dev_password@localhost:5432/cosmic_watch_db
REDIS_URL=redis://localhost:6379/0
NASA_API_KEY=your-nasa-key
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
EOF

# Install dependencies
pip install -r requirements.txt

# Create local database
createdb -U cosmicwatch cosmic_watch_db

# Run migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Create .env.local
cat > .env.local << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
EOF

# Install dependencies
npm install

# Start dev server
npm run dev
```

---

## 🔐 Security Best Practices

### Never Commit Secrets

```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore
```

### Use Secrets Management in Production

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name cosmic-watch/db-password \
  --secret-string "your-secure-password"
```

**Google Cloud Secret Manager:**
```bash
gcloud secrets create cosmic-watch-db-password \
  --replication-policy="automatic"
```

**HashiCorp Vault:**
```bash
vault write secret/cosmic-watch \
  DATABASE_URL=postgresql://... \
  NASA_API_KEY=...
```

### Rotate Secrets Regularly

- Change `SECRET_KEY` every 90 days
- Rotate NASA_API_KEY when compromised
- Update DB passwords quarterly

---

## 📋 Environment Variable Checklist

### Required for Backend
- [ ] `SECRET_KEY` - Generated and set
- [ ] `DATABASE_URL` - Points to valid PostgreSQL
- [ ] `NASA_API_KEY` - Valid NASA API key
- [ ] `REDIS_URL` - Redis instance accessible

### Required for Frontend
- [ ] `REACT_APP_API_URL` - Correct API endpoint
- [ ] `REACT_APP_ENV` - Set to environment

### Optional but Recommended
- [ ] `SMTP_HOST` - For email notifications
- [ ] `SENTRY_DSN` - For error tracking
- [ ] `LOG_LEVEL` - For debugging

---

## 🧪 Test Connection

### Verify Backend Connectivity

```bash
# Check database
docker-compose exec backend python -c "
from app.core.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('✅ Database connected')
"

# Check Redis
docker-compose exec backend python -c "
import redis
r = redis.from_url('redis://redis:6379/0')
r.ping()
print('✅ Redis connected')
"

# Check NASA API
docker-compose exec backend python -c "
import httpx
resp = httpx.get('https://api.nasa.gov/neo/rest/v1/neo/browse?api_key=YOUR_KEY')
print(f'✅ NASA API status: {resp.status_code}')
"
```

### Verify Frontend Connectivity

```bash
# Check API connection
curl http://localhost:8000/health

# Check CORS
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     http://localhost:8000/health
```

---

## 🚨 Troubleshooting

### Issue: "DATABASE_URL" not found

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check it's being loaded
cat .env | grep DATABASE_URL
```

### Issue: NASA API Key Invalid

**Solution:**
```bash
# Verify key format
echo $NASA_API_KEY

# Test API directly
curl "https://api.nasa.gov/neo/rest/v1/neo/browse?api_key=$NASA_API_KEY"
```

### Issue: Redis Connection Failed

**Solution:**
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
# Should output: PONG
```

### Issue: Database Connection Timeout

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U cosmicwatch -c "SELECT 1"
```

---

## 📚 References

- [NASA API Docs](https://api.nasa.gov/)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html)
- [Redis Connection](https://redis.io/commands/ping/)
- [FastAPI Environment Variables](https://fastapi.tiangolo.com/deployment/concepts/#environment-variables)
- [React Environment Variables](https://create-react-app.dev/docs/adding-custom-environment-variables/)

---

**Last Updated**: 2024
**Questions?** Check README.md or create an issue on GitHub
