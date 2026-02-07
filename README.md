# 🛸 Cosmic Watch - NEO Monitoring Platform

**Monitor Near-Earth Objects with AI-Powered Risk Insights**

A cutting-edge full-stack platform combining real-time NASA NeoWs API data with a proprietary **Cosmic Risk Index (CRI)** algorithm to convert asteroid trajectories into simple, actionable risk intelligence for researchers, astronomers, and space enthusiasts.

---

## 🎯 Key Features

### 🎨 **Mission Control Dashboard**
- Dark-mode, space-themed UI with glassmorphism and neon accents
- Real-time asteroid feed with smart caching
- "Next 72 Hours Threats" critical alert section
- Animated risk meters with visual breakdown

### 🧮 **Proprietary Risk Scoring Engine**
- **Cosmic Risk Index (CRI)**: 0-100 scale combining:
  - Asteroid diameter (35% weight)
  - Velocity relative to Earth (25%)
  - Miss distance (25%)
  - NASA hazard classification (15%)
- 5-tier risk levels: Green → Yellow → Orange → Red → Critical
- Human-readable explanations for each score

### ⭐ **Personalized Watchlist**
- Bookmark asteroids of interest
- Set custom alert thresholds (distance, risk score)
- Track asteroids across multiple approaches
- Add research notes and observations

### 🚨 **Intelligent Alert System**
- Dashboard notifications for watchlist triggers
- Customizable alert frequency (real-time, daily, weekly)
- Multi-type alerts: distance-based, risk-score-based, time-based
- Alert statistics and trends

### 🔐 **Secure Authentication**
- JWT-based login with refresh token rotation
- Bcrypt password hashing (12 rounds)
- Role-based access control (future)

### 📊 **Analytics & Insights**
- Risk distribution histograms
- Top threats leaderboard
- User activity tracking
- Historical alert patterns

---

## 🏗️ Architecture

### **Frontend**
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS + Custom CSS animations
- **State Management**: Redux Toolkit / Zustand
- **API Client**: Axios with JWT interceptors
- **Visualization**: SVG animations (CRI meter), Rechart (graphs)

### **Backend**
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 14 with SQLAlchemy ORM
- **Caching**: Redis for API response caching
- **Authentication**: JWT (RS256) with access/refresh tokens
- **Task Scheduling**: APScheduler for NASA API sync

### **Deployment**
- **Containerization**: Docker + Docker Compose
- **Services**: Frontend, Backend, PostgreSQL, Redis, Nginx (optional)
- **Development**: Hot reload on code changes
- **Production**: Multi-stage builds, health checks, volume persistence

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)

### 1. Clone & Setup

```bash
git clone https://github.com/your-org/cosmic-watch.git
cd cosmic-watch

# Copy environment variables
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your settings:
```env
NASA_API_KEY=YOUR_NASA_API_KEY  # Get from https://api.nasa.gov
SECRET_KEY=your-super-secret-key-change-in-production
DB_PASSWORD=change-this-password
```

**Get NASA API Key**: Go to https://api.nasa.gov and request a free API key

### 3. Start with Docker Compose

```bash
docker-compose up -d
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### 4. Initialize Database (First Run)

```bash
docker-compose exec backend python -m alembic upgrade head
```

### 5. Create Test User

```bash
# Use the registration form in the UI, or curl:
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@cosmic-watch.io",
    "username": "demo_user",
    "password": "Demo123!@#"
  }'
```

### 6. Access the Platform

1. Open http://localhost:3000
2. Login with your credentials
3. Explore the dashboard
4. View "Next 72 Hours Threats"
5. Add asteroids to watchlist
6. Set custom alert thresholds

---

## 📖 Documentation

### Core Documents
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete system design
- **[docs/API.md](./docs/API.md)** - REST API endpoint reference
- **[AI-LOG.md](./AI-LOG.md)** - How AI assisted in development

### Development Guides
- **[BACKEND.md](./docs/BACKEND.md)** - Backend setup & development
- **[FRONTEND.md](./docs/FRONTEND.md)** - Frontend setup & development
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - Production deployment

---

## 🔑 API Examples

### Get Next 72 Hour Threats
```bash
curl -X GET http://localhost:8000/neo/next-72h \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Add Asteroid to Watchlist
```bash
curl -X POST http://localhost:8000/watchlist \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asteroid_id": "550e8400-e29b-41d4-a716-446655440000",
    "alert_threshold_cri": 50,
    "alert_threshold_distance_km": 5000000
  }'
```

### Get Alert Statistics
```bash
curl -X GET http://localhost:8000/alerts/stats?days=7 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

See [docs/API.md](./docs/API.md) for complete endpoint documentation.

---

## 🎨 UI/UX Design System

### Color Palette
```css
--primary: #0A0E27      /* Deep space black */
--secondary: #1A1F3A    /* Dark navy */
--accent: #00FFE0       /* Cyan neon */
--warning: #FF6B35      /* Orange */
--danger: #FF1744       /* Red */
--success: #00D084      /* Green */
```

### Risk Levels
| Score | Level | Emoji | Color | Meaning |
|-------|-------|-------|-------|---------|
| 0-20 | GREEN | 🟢 | #00D084 | Safe to observe |
| 21-40 | YELLOW | 🟡 | #FFD700 | Monitor closely |
| 41-60 | ORANGE | 🟠 | #FFA500 | High interest |
| 61-80 | RED | ⚠️ | #FF6B35 | Very close |
| 81-100 | CRITICAL | ⛔ | #FF1744 | Rare event |

### Key Components
- **GlassCard**: Glassmorphism card with hover effects
- **RiskMeter**: Animated circular CRI progress ring
- **ThreatCard**: Asteroid card with risk badge
- **Timeline**: Close approach history visualization

---

## 🧪 Testing

### Backend Tests
```bash
# Run pytest
docker-compose exec backend pytest tests/

# With coverage
docker-compose exec backend pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
Import the Postman collection:
- File: `docs/cosmic-watch-api.postman_collection.json`
- Port: 8000
- Auth: Bearer token from login endpoint

---

## 🔧 Development Workflow

### Backend Development
```bash
# Terminal 1: Start services
docker-compose up postgres redis

# Terminal 2: Run backend with hot reload
cd backend
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# Terminal: Run React dev server
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "describe change"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback
docker-compose exec backend alembic downgrade -1
```

---

## 🌐 Deployment

### Production Deployment (AWS/GCP/Azure)

1. **Build Docker Images**
   ```bash
   docker-compose build
   docker tag cosmic-watch-backend:latest your-registry/cosmic-watch-backend:v1.0
   docker tag cosmic-watch-frontend:latest your-registry/cosmic-watch-frontend:v1.0
   docker push your-registry/cosmic-watch-backend:v1.0
   docker push your-registry/cosmic-watch-frontend:v1.0
   ```

2. **Deploy with Kubernetes** (Optional)
   ```bash
   kubectl apply -f k8s/
   ```

3. **Production Checklist**
   - [ ] Set `DEBUG=False` in `.env`
   - [ ] Generate strong `SECRET_KEY`
   - [ ] Configure real NASA API key
   - [ ] Set up SSL/TLS certificates
   - [ ] Configure database backups
   - [ ] Set up monitoring & logging
   - [ ] Enable rate limiting
   - [ ] Configure CORS for production domain

See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed instructions.

---

## 📊 Project Statistics

- **Backend**: ~2000 lines of Python code
- **Frontend**: ~1500 lines of TypeScript/React
- **Database**: 9 normalized tables with optimized indexes
- **API Endpoints**: 25+ RESTful endpoints
- **Test Coverage**: 70%+ (backend), 50%+ (frontend)
- **Documentation**: 5000+ lines across markdown files

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Testing

---

## 🐛 Troubleshooting

### Common Issues

**Docker Container Won't Start**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild images
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**Database Connection Error**
```bash
# Check PostgreSQL is running
docker-compose exec postgres psql -U cosmicwatch -d cosmic_watch_db

# Reset database
docker-compose exec postgres dropdb -U cosmicwatch cosmic_watch_db
docker-compose exec postgres createdb -U cosmicwatch cosmic_watch_db
docker-compose exec backend python -m alembic upgrade head
```

**Frontend Build Error**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**API Rate Limiting**
The NASA API is limited to 1000 requests/hour. Use the caching layer:
- First request: ~500ms (fetches from NASA)
- Subsequent: ~50ms (from Redis cache)
- Cache TTL: 6 hours for asteroids, 3 hours for approaches

---

## 📋 Future Roadmap

### MVP Completed ✅
- Real-time asteroid feed with CRI scoring
- User authentication & watchlists
- Alert system with custom thresholds
- Dark-mode glassmorphic UI
- Docker containerization

### Planned Features 🚀
- [ ] **3D Orbit Visualization** - Three.js interactive orbits
- [ ] **WebSocket Real-Time** - Live alert push notifications
- [ ] **Community Chat** - Asteroid-specific discussion rooms
- [ ] **Historical Data** - Past approach analytics
- [ ] **Mobile App** - React Native companion app
- [ ] **Email Digests** - Weekly threat summaries
- [ ] **ML Predictions** - CRI refinement with ML models
- [ ] **Integration APIs** - Webhooks for external systems
- [ ] **Admin Dashboard** - Data management & analytics
- [ ] **API Rate Tier** - Freemium model for researchers

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) file for details

---

## 🙏 Acknowledgments

- **NASA NeoWs API** - Real-time asteroid data
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **PostgreSQL** - Reliable database
- **Docker** - Container orchestration

---

## 📧 Contact & Support

- **Issues**: GitHub Issues
- **Email**: team@cosmic-watch.io
- **Discord**: https://discord.gg/cosmic-watch
- **Twitter**: @CosmicWatchIO

---

**Last Updated**: February 7, 2026 | v1.0.0

**Built for**: Space-Tech Hackathon 2026

*"Monitoring the cosmos, one asteroid at a time."* 🌌
