# Cosmic Watch - Quick Start Guide

## 🎯 60-Second Setup

### Step 1: Clone the Project
```bash
git clone https://github.com/AstroSentinel/cosmic-watch.git
cd cosmic-watch
```

### Step 2: Set Environment
```bash
cp .env.example .env
# Edit .env and add your NASA_API_KEY from https://api.nasa.gov
```

### Step 3: Start Everything
```bash
docker-compose up -d
```

### Step 4: Access Platform
- **UI**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### Step 5: Create Account & Login
```bash
# Use the registration form in the UI
# Email: test@example.com
# Password: TestPassword123
```

---

## 📱 What You Can Do Immediately

### Dashboard
- ✅ View "Next 72 Hours Threats" - asteroids approaching with high risk
- ✅ See risk scores calculated with proprietary CRI algorithm
- ✅ Monitor animated risk meters

### Watchlist
- ✅ Add asteroids to track
- ✅ Set custom alert thresholds (distance, risk score)
- ✅ Add personal notes

### Alerts
- ✅ View triggered notifications
- ✅ Filter by type or read status
- ✅ Get alert statistics

### Search
- ✅ Find specific asteroids by name
- ✅ View physical properties
- ✅ Check all close approaches

---

## 🔌 API Quick Test

### Get Auth Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

### Get Next 72h Threats
```bash
curl -X GET http://localhost:8000/neo/next-72h \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Add to Watchlist
```bash
curl -X POST http://localhost:8000/watchlist \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "asteroid_id": "550e8400-e29b-41d4-a716-446655440000",
    "alert_threshold_cri": 50,
    "alert_threshold_distance_km": 5000000
  }'
```

See [docs/API.md](./docs/API.md) for full API reference.

---

## 🐳 Docker Commands

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs postgres
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart backend frontend
```

### Access Database
```bash
docker-compose exec postgres psql -U cosmicwatch -d cosmic_watch_db
```

### Run Backend Tests
```bash
docker-compose exec backend pytest tests/
```

---

## 🚨 If Something Goes Wrong

### Backend Won't Start
```bash
# View error logs
docker-compose logs backend

# Rebuild
docker-compose down
docker-compose build --no-cache backend
docker-compose up backend
```

### Can't Connect to API
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check PostgreSQL is running
nc -zv localhost 5432

# Check Redis is running
nc -zv localhost 6379
```

### Database Issues
```bash
# Reset database (CAUTION: Deletes all data)
docker-compose down -v
docker-compose up -d postgres
docker-compose up backend  # Migrations auto-run
```

### Frontend White Screen
```bash
# Clear browser cache
# Hard refresh: Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
# In browser DevTools: Application > Clear Storage

# Rebuild frontend
docker-compose restart frontend
```

---

## 📚 Key Files to Understand

| File | Purpose |
|------|---------|
| `README.md` | Project overview & features |
| `ARCHITECTURE.md` | System design & technical decisions |
| `docs/API.md` | REST API full reference |
| `AI-LOG.md` | How AI assisted development |
| `docker-compose.yml` | Service orchestration config |
| `backend/main.py` | FastAPI application entry point |
| `backend/app/models/models.py` | Database schema |
| `backend/app/utils/risk_calculator.py` | CRI algorithm implementation |
| `frontend/src/App.tsx` | React main component |
| `frontend/src/pages/Dashboard.tsx` | Dashboard page |

---

## 🎓 Learning Path

If you're new to the codebase:

### 5 Minutes
1. Read this Quick Start Guide
2. Start the project with Docker
3. Create an account and explore UI

### 30 Minutes
1. Read [README.md](./README.md)
2. Check out the dashboard and alert system
3. Explore API docs at http://localhost:8000/docs

### 1 Hour
1. Study [ARCHITECTURE.md](./ARCHITECTURE.md)
2. Review [docs/API.md](./docs/API.md)
3. Try API calls with curl or Postman

### 2 Hours
1. Explore backend code: `backend/app/services/`
2. Check `backend/app/utils/risk_calculator.py` for CRI algorithm
3. Review React components: `frontend/src/components/`

### 4 Hours
1. Deep dive into database models: `backend/app/models/models.py`
2. Understand authentication flow: `backend/app/core/security.py`
3. Study API routes: `backend/app/routes/`

---

## 💡 Tips & Tricks

### Enable Debug Mode
```bash
# Edit .env
DEBUG=True

# Restart backend
docker-compose restart backend
```

### View Real-Time Logs
```bash
# Terminal 1: Backend logs
docker-compose logs -f backend

# Terminal 2: Frontend logs
docker-compose logs -f frontend

# Terminal 3: Database logs
docker-compose logs -f postgres
```

### Test with Test User
```bash
# Pre-populate with sample data
docker-compose exec backend python -c "
from app.services.auth_service import AuthService
from app.core.database import SessionLocal
from app.schemas.schemas import UserRegisterRequest

db = SessionLocal()
try:
    AuthService.register_user(db, UserRegisterRequest(
        email='demo@cosmic-watch.io',
        username='demo_astronomer',
        password='Demo123!@#'
    ))
    print('✅ Demo user created')
except:
    print('User already exists')
"
```

### Monitor Database Growth
```bash
docker-compose exec postgres psql -U cosmicwatch cosmic_watch_db -c "
SELECT 
  schemaname,tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

---

## 🎯 Next Steps

1. **Customize CRI Algorithm** - Adjust weights in `backend/app/utils/risk_calculator.py`
2. **Add More Asteroids** - Increase NASA API sync frequency
3. **Extend Alerts** - Add email notifications or SMS
4. **Beautiful Reports** - Create historical trending charts
5. **Mobile App** - Build React Native version

---

## 📞 Support

- **Docs**: Check [README.md](./README.md) and [ARCHITECTURE.md](./ARCHITECTURE.md)
- **API Reference**: Visit http://localhost:8000/docs
- **Issues**: Check existing GitHub issues
- **Community**: Join Discord (link in README)

---

**Happy monitoring! 🛸🌌**
