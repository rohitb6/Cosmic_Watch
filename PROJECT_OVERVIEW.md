# Cosmic Watch - Complete Project Overview

## 🌟 Project Summary

**Cosmic Watch** is a full-stack web application that monitors Near-Earth Objects (NEOs) using NASA's NeoWs API, converting complex asteroid trajectory data into actionable risk insights through a proprietary Risk Scoring Engine.

**Repository**: AstroSentinel/cosmic-watch  
**Status**: MVP Complete ✅  
**Latest Update**: 2024  

---

## 📊 Project Statistics

### Code Base
- **Total Files**: 45+ files
- **Backend**: ~3,500 lines of Python (FastAPI, SQLAlchemy)
- **Frontend**: ~2,000 lines of TypeScript/React
- **Configuration**: ~500 lines (Docker, config files)
- **Documentation**: ~2,500 lines (Architecture, API, guides)

### Architecture
- **Backend Services**: 4 (Auth, Asteroid, Watchlist, Alert)
- **Database Tables**: 9 (Users, Asteroids, Approaches, Alerts, etc.)
- **API Endpoints**: 25+ (Rest + Health)
- **React Pages**: 5 (Dashboard, Detail, Watchlist, Alerts, Auth)
- **React Components**: 10+ (Layout, RiskMeter, Cards, etc.)
- **Docker Services**: 6 (PostgreSQL, Redis, Backend, Frontend, Nginx, Healthcheck)

---

## 🗂️ Directory Structure

```
cosmic-watch/
│
├── backend/                          # FastAPI Application
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py            # Settings management
│   │   │   ├── database.py          # SQLAlchemy setup
│   │   │   └── security.py          # JWT + password handling
│   │   ├── models/
│   │   │   └── models.py            # 9 database tables
│   │   ├── schemas/
│   │   │   └── schemas.py           # 25+ Pydantic models
│   │   ├── services/
│   │   │   ├── auth_service.py      # User management
│   │   │   ├── asteroid_service.py  # NEO operations
│   │   │   ├── watchlist_service.py # Watchlist management
│   │   │   └── alert_service.py     # Alert system
│   │   ├── routes/
│   │   │   ├── auth.py              # /auth endpoints
│   │   │   ├── asteroids.py         # /neo endpoints
│   │   │   ├── watchlist.py         # /watchlist endpoints
│   │   │   └── alerts.py            # /alerts endpoints
│   │   └── utils/
│   │       └── risk_calculator.py   # CRI algorithm
│   ├── main.py                       # FastAPI app
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend container
│   └── .env.example                  # Configuration template
│
├── frontend/                         # React Application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   └── Layout.tsx       # Navigation + sidebar
│   │   │   └── Dashboard/
│   │   │       └── RiskMeter.tsx    # Animated SVG meter
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx        # Main page
│   │   │   ├── AsteroidDetail.tsx   # Detail view
│   │   │   ├── Watchlist.tsx        # User watchlist
│   │   │   ├── Alerts.tsx           # Alert system
│   │   │   └── Auth/
│   │   │       ├── Login.tsx
│   │   │       └── Register.tsx
│   │   ├── hooks/
│   │   │   ├── useAsteroids.ts      # Asteroid operations
│   │   │   └── useAuth.ts           # Auth management
│   │   ├── utils/
│   │   │   ├── api.ts               # Axios + JWT
│   │   │   ├── riskCalculator.ts    # Client-side CRI
│   │   │   └── formatters.ts        # Date/distance formatting
│   │   ├── styles/
│   │   │   └── globals.css          # Glassmorphism + animations
│   │   ├── App.tsx                  # React Router setup
│   │   └── main.tsx                 # React entry point
│   ├── index.html                   # HTML template
│   ├── package.json                 # Node dependencies
│   ├── vite.config.ts               # Build configuration
│   ├── tailwind.config.js           # Tailwind setup
│   ├── tsconfig.json                # TypeScript config
│   ├── Dockerfile                   # Frontend container
│   └── .env.example                 # Frontend config template
│
├── docs/
│   ├── API.md                       # API documentation
│   ├── POSTMAN_COLLECTION.md        # Postman guide
│   ├── ENVIRONMENT_SETUP.md         # Configuration guide
│   └── TESTING_GUIDE.md             # Testing information
│
├── docker-compose.yml               # Service orchestration
├── ARCHITECTURE.md                  # System design document
├── QUICKSTART.md                    # Quick reference guide
├── CONTRIBUTING.md                  # Contribution guidelines
├── AI-LOG.md                        # AI development transparency
├── README.md                        # Project README
├── .env.example                     # Main environment template
└── .gitignore                       # Git exclusions
```

---

## 🔌 Core Components

### Backend Stack
```
FastAPI 0.104.1          → Async web framework
SQLAlchemy 2.0.23        → ORM layer
PostgreSQL 14            → Primary database
Redis 7-alpine           → Caching layer
Pydantic 2.5.0           → Data validation
PyJWT                    → JWT authentication
passlib[bcrypt]          → Password hashing
httpx                    → Async HTTP client
```

### Frontend Stack
```
React 18.2.0             → UI framework
TypeScript 5.3.3         → Type safety
Vite 5.0.2               → Build tool
Tailwind CSS 3.4.1       → Styling
Axios 1.6.2              → HTTP client
React Router 6           → Navigation
```

### Deployment Stack
```
Docker 20.x              → Containerization
Docker Compose 3.8       → Orchestration
PostgreSQL 14-alpine     → Database
Redis 7-alpine           → Cache
Node.js 18-alpine        → Frontend runtime
Python 3.10-slim         → Backend runtime
```

---

## ⚙️ Key Features

### 1. **Cosmic Risk Index (CRI) Algorithm**
Proprietary algorithm combining:
- **Diameter** (35% weight) → Size estimation
- **Velocity** (25% weight) → Impact energy
- **Miss Distance** (25% weight) → Proximity risk
- **Hazard Flag** (15% weight) → NASA classification

Formula: Sigmoid normalization with weighted sum → 0-100 scale

Risk Levels:
- 🟢 **Green** (0-20): Safe
- 🟡 **Yellow** (21-40): Monitor
- 🟠 **Orange** (41-60): Watch Closely
- 🔴 **Red** (61-80): High Risk
- ⚫ **Critical** (81-100): Extreme Danger

### 2. **Real-Time NEO Monitoring**
- Live NASA NeoWs API integration
- 6-hour sync cycle for asteroids
- 30-minute alert check cycle
- 24/7 threat detection

### 3. **Personalized Watchlist**
- Track specific asteroids
- Custom alert thresholds
- Personal notes per asteroid
- Risk score tracking

### 4. **Advanced Alert System**
- Risk score alerts (customizable threshold)
- Distance alerts (close approach monitoring)
- 72-hour advance warning system
- Unread notification tracking

### 5. **Glassmorphic Space Theme UI**
- Dark mode optimized
- Neon cyan (#00FFE0) accents
- Backdrop blur effects
- Animated risk meters
- Responsive design (desktop-first)

### 6. **Secure Authentication**
- JWT token-based auth
- Access tokens (15min expiry)
- Refresh tokens (7 days)
- Bcrypt password hashing (12 rounds)
- Automatic token refresh on API calls

### 7. **Performance Optimized**
- Redis caching (6h TTL asteroids, 3h approaches)
- Database connection pooling (10-50 connections)
- Indexed queries on fast path
- Lazy-loaded asteroid details
- Client-side CRI calculation

---

## 📊 Database Schema

### Core Tables
1. **users** - User accounts with preferences
2. **asteroids** - NEO catalog from NASA
3. **close_approaches** - Approach records with calculated CRI
4. **watchlist** - User-asteroid relationships with alert thresholds
5. **alerts** - Triggered notifications
6. **risk_scoring_logs** - CRI calculation analytics
7. **nasa_api_cache** - Response caching
8. **user_preferences** - Custom settings per user

---

## 🔌 API Endpoints (25+)

### Authentication (5)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `GET /auth/me` - Current user
- `POST /auth/logout` - Session logout

### Asteroids (6)
- `GET /neo/feed` - Paginated asteroid list
- `GET /neo/next-72h` - Threats in 72 hours
- `GET /neo/{id}` - Asteroid details
- `GET /neo/search` - Search by name
- `GET /neo/today` - Today's approaches
- `POST /neo/sync` - Force NASA sync

### Watchlist (5)
- `GET /watchlist` - User's watchlist
- `POST /watchlist` - Add asteroid
- `PUT /watchlist/{id}` - Update thresholds
- `DELETE /watchlist/{id}` - Remove asteroid
- `GET /watchlist/{id}/status` - Check status

### Alerts (5)
- `GET /alerts` - List alerts
- `PATCH /alerts/{id}/read` - Mark as read
- `DELETE /alerts/{id}` - Delete alert
- `GET /alerts/stats` - Alert statistics
- `POST /alerts/check-thresholds` - Check watchlist

### System (1)
- `GET /health` - Health check

---

## 🎨 UI/UX Design System

### Color Palette
```
Primary: #00FFE0 (Neon Cyan)
Dark Background: #0a0e27 (Deep Blue)
Card: rgba(255, 255, 255, 0.05)
Danger: #FF1744 (Red)
Success: #00FF00 (Green)
```

### Component Library
- **Layout**: Sidebar navigation, user menu
- **Cards**: Asteroid cards, alert cards, threat cards
- **Inputs**: Form fields, search bar
- **Buttons**: Primary, secondary, danger variants
- **Meters**: Animated SVG risk meter
- **Modals**: Confirmation, detail views
- **Badges**: Risk level indicators

### Animations
- Pulse glow effect on hover
- Floating animation on cards
- Orbit animation for asteroids
- Smooth transitions on theme change
- Loading skeleton screens

---

## 🚀 Deployment

### Docker Compose Services
1. **PostgreSQL** - Database (port 5432)
2. **Redis** - Cache (port 6379)
3. **backend** - FastAPI (port 8000)
4. **frontend** - React (port 3000)
5. **nginx** - Reverse proxy (optional)
6. **healthchecks** - Monitoring

### Health Checks
- Backend: HTTP /health
- Database: psql connection
- Redis: redis-cli ping
- Frontend: HTTP 200 on /

### Volumes
- `postgres_data`: Database persistence
- `redis_data`: Cache persistence
- `backend_logs`: Application logs

---

## 📚 Documentation Files

| File | Purpose | Length |
|------|---------|--------|
| [README.md](./README.md) | Project overview | 600+ lines |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design | 650+ lines |
| [docs/API.md](./docs/API.md) | API reference | 400+ lines |
| [docs/TESTING_GUIDE.md](./docs/TESTING_GUIDE.md) | Testing strategies | 300+ lines |
| [docs/ENVIRONMENT_SETUP.md](./docs/ENVIRONMENT_SETUP.md) | Configuration guide | 400+ lines |
| [docs/POSTMAN_COLLECTION.md](./docs/POSTMAN_COLLECTION.md) | API testing | 250+ lines |
| [QUICKSTART.md](./QUICKSTART.md) | 60-second setup | 200+ lines |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Dev guidelines | 50+ lines |
| [AI-LOG.md](./AI-LOG.md) | AI transparency | 500+ lines |

---

## ✅ Completed Features

- ✅ FastAPI backend with service layer architecture
- ✅ React frontend with TypeScript
- ✅ PostgreSQL with normalized schema
- ✅ JWT authentication with token refresh
- ✅ Proprietary Cosmic Risk Index algorithm
- ✅ Real-time NASA API integration
- ✅ Redis caching layer (6h/3h TTL)
- ✅ Personalized watchlist system
- ✅ Advanced alert system (distance, risk score)
- ✅ Glassmorphic space-themed UI
- ✅ Responsive design (desktop, mobile)
- ✅ Docker containerization (6 services)
- ✅ Comprehensive documentation
- ✅ Transparent AI development log
- ✅ Environment configuration system

---

## 🚧 Future Enhancements

### Phase 2 (Post-MVP)
- [ ] WebSocket real-time alerts (Socket.io)
- [ ] 3D asteroid orbit visualization (Three.js)
- [ ] Email digest notifications
- [ ] Community discussion forums
- [ ] Advanced charting and analytics
- [ ] Mobile app (React Native)

### Phase 3 (Production)
- [ ] ML-based CRI refinement
- [ ] Internationalization (i18n)
- [ ] Admin dashboard
- [ ] API rate-tiering
- [ ] Advanced search filters
- [ ] Historical trend analysis

---

## 🧪 Testing Coverage

### Backend Tests
- Unit tests: Auth, Asteroid, Watchlist, Alert services
- Integration tests: API endpoints, database operations
- Coverage goal: 80%+

### Frontend Tests
- Component tests: React Testing Library
- Hook tests: useAsteroids, useAuth
- Coverage goal: 70%+

### E2E Tests
- Cypress tests: Full user workflows
- Load tests: K6 performance testing

---

## 📈 Performance Metrics

### Target Performance
- **API Response Time**: < 200ms P95
- **Dashboard Load**: < 2 seconds
- **Search Results**: < 500ms
- **Alert Triggering**: < 1 minute
- **Concurrent Users**: 1000+ (with horizontal scaling)

### Optimization Strategies
- Database indexes on frequently-queried columns
- Redis caching for API responses
- Connection pooling for database
- Frontend code splitting by route
- Image optimization and lazy loading

---

## 🔐 Security Features

- JWT token-based authentication
- Bcrypt password hashing (12 rounds)
- CORS middleware with origin whitelist
- Trusted Host validation
- SQL injection prevention (SQLAlchemy ORM)
- HTTPS ready (TLS/SSL support)
- Rate limiting infrastructure
- Secure password requirements

---

## 🎯 Getting Started

### Quick Start (Docker)
```bash
git clone https://github.com/AstroSentinel/cosmic-watch.git
cd cosmic-watch
cp .env.example .env
# Add your NASA_API_KEY to .env
docker-compose up -d
# Access at http://localhost:3000
```

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## 📞 Support & Resources

- **Documentation**: See [README.md](./README.md)
- **API Docs**: http://localhost:8000/docs
- **Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Quick Help**: See [QUICKSTART.md](./QUICKSTART.md)
- **Testing**: See [docs/TESTING_GUIDE.md](./docs/TESTING_GUIDE.md)

---

## 📄 License

This project is part of the AstroSentinel initiative. See LICENSE file for details.

---

## 🙏 Acknowledgments

- **NASA NeoWs API** - Near-Earth Object data
- **FastAPI** - Modern Python web framework
- **React** - UI framework
- **PostgreSQL** - Trusted database
- **Docker** - Container orchestration

---

**Last Updated**: 2024  
**Maintainer**: AstroSentinel Team  
**Status**: Active Development ✅

*"Turning cosmic data into actionable insights"* 🛸🌌
