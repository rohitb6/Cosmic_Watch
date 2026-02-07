# COSMIC WATCH - Complete System Architecture

## **1. System Overview**

**Cosmic Watch** is a space-tech platform that transforms raw NASA Near-Earth Objects (NEOs) data into actionable risk intelligence with a stunning dark-mode, glassmorphic UI.

### **Core Value Proposition**
- **Real-time Asteroid Monitoring**: Live data from NASA NeoWs API with smart caching
- **Cosmic Risk Index (CRI)**: Proprietary algorithm converting multiple factors into 0-100 risk scores
- **Personalized Watchlists**: Users bookmark asteroids and set custom alerts
- **Mission Control Dashboard**: Space-themed interface with animated visualizations
- **Smart Notifications**: "Next 72 Hours Threats" with actionable insights

---

## **2. Architectural Components**

### **2.1 Frontend Stack**
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS + Custom CSS animations
- **State Management**: Redux Toolkit + RTK Query
- **3D Visualization**: Three.js for orbit visualization
- **Real-time**: Socket.io for live updates
- **Design Pattern**: Glassmorphism + Neon accents, Space-themed

### **2.2 Backend Stack**
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 14+
- **Caching**: Redis for API response caching
- **Authentication**: JWT tokens with refresh rotation
- **Rate Limiting**: Token bucket algorithm
- **Background Jobs**: APScheduler for periodic NASA API syncs

### **2.3 Database Layer**
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Schema**: Normalized relational design
- **Indexes**: Optimized on frequent queries (asteroid_id, user_id, risk_score)

### **2.4 Deployment**
- **Containerization**: Docker + Docker Compose
- **Services**: Frontend, Backend, PostgreSQL, Redis, Nginx
- **Environment**: Support for dev, staging, production

---

## **3. Database Schema**

### **Users Table**
```
users
├── id (UUID, primary key)
├── email (unique, indexed)
├── username (unique)
├── password_hash (bcrypt)
├── created_at
├── updated_at
├── is_active
└── preferences (JSON: theme, notification_frequency, alert_threshold)
```

### **Asteroids Table**
```
asteroids (synced from NASA NeoWs API)
├── id (UUID, primary key)
├── neo_id (NASA ID, unique, indexed)
├── name (asteroid name)
├── diameter_min (meters)
├── diameter_max (meters)
├── is_hazardous (boolean)
├── absolute_magnitude
├── estimated_diameter_km
├── last_updated (NASA data timestamp)
├── nasa_synced_at (our last fetch)
```

### **Close Approaches Table**
```
close_approaches (per asteroid, sorted by date)
├── id (UUID, primary key)
├── asteroid_id (FK)
├── closest_approach_date (indexed)
├── approach_velocity_kmh
├── miss_distance_km
├── distance_to_earth_km
├── is_conjunct (boolean: lunar orbits, etc)
├── nasa_synced_at
```

### **Watchlist Table**
```
watchlists
├── id (UUID, primary key)
├── user_id (FK, indexed)
├── asteroid_id (FK)
├── created_at
├── alert_threshold_distance_km
├── alert_threshold_cri_score
├── custom_notes (user annotations)
```

### **Alerts Table**
```
alerts (triggered notifications)
├── id (UUID, primary key)
├── user_id (FK, indexed)
├── asteroid_id (FK)
├── alert_type (enum: DISTANCE, RISK_SCORE, APPROACH_24H)
├── triggered_at
├── is_read (boolean)
├── cri_score_at_trigger
├── notification_sent_via (email, dashboard, push)
```

### **Risk Scoring Logs Table** (analytics)
```
risk_scoring_logs
├── id (UUID, primary key)
├── asteroid_id (FK)
├── close_approach_id (FK)
├── cri_score (0-100)
├── calculation_timestamp
├── component_scores (JSON: diameter_factor, velocity_factor, distance_factor)
```

---

## **4. Cosmic Risk Index (CRI) Formula**

**Unique algorithm combining multiple factors:**

```
CRI = (Diameter_Score × 0.35) + (Velocity_Score × 0.25) + 
      (Distance_Score × 0.25) + (Hazard_Bonus × 0.15)

where:
- Diameter_Score = sigmoid((diameter_km / 1) × 100)  // Impact potential
- Velocity_Score = sigmoid((velocity_kmh / 30000) × 100)  // Speed factor
- Distance_Score = sigmoid((1 / (miss_distance_km + 1)) × 100)  // Proximity
- Hazard_Bonus = +15 if NASA flagged as hazardous, else 0

CRI ∈ [0, 100] normalized output
```

**Risk Categories:**
- 0-20: **Green** - "Safe to observe 🟢"
- 21-40: **Yellow** - "Monitor closely 🟡"
- 41-60: **Orange** - "High interest 🟠"
- 61-80: **Red** - "Very close approach ⚠️"
- 81-100: **Critical** - "Rare celestial event ⛔"

---

## **5. Backend API Structure**

All endpoints require JWT auth (except `/auth/register`, `/auth/login`, `/health`).

### **5.1 Authentication Endpoints**

| Method | Endpoint | Purpose | Payload |
|--------|----------|---------|---------|
| POST | `/auth/register` | Register new user | `{email, username, password}` |
| POST | `/auth/login` | Get JWT token | `{email, password}` |
| POST | `/auth/refresh` | Refresh access token | `{refresh_token}` |
| POST | `/auth/logout` | Invalidate token | - |
| GET | `/auth/me` | Get current user | - |

### **5.2 NEO Feed Endpoints**

| Method | Endpoint | Purpose | Query Params |
|--------|----------|---------|--------------|
| GET | `/neo/feed` | Get paginated asteroid list | `page=1&limit=20&sort=risk_desc\|date_asc` |
| GET | `/neo/today` | Today's approaching asteroids | - |
| GET | `/neo/next-72h` | Critical: Next 72 hours | `threat_level=high\|medium` |
| GET | `/neo/{asteroid_id}` | Single asteroid details | - |
| GET | `/neo/{asteroid_id}/approaches` | Close approach history | `start_date=2025-01-01&end_date=2025-12-31` |
| GET | `/neo/search` | Full-text search asteroids | `q=Apophis&limit=10` |

### **5.3 Watchlist Endpoints**

| Method | Endpoint | Purpose | Payload |
|--------|----------|---------|---------|
| GET | `/watchlist` | Get user's watchlist | - |
| POST | `/watchlist` | Add asteroid to watchlist | `{asteroid_id, alert_distance_km, alert_cri}` |
| DELETE | `/watchlist/{asteroid_id}` | Remove from watchlist | - |
| PUT | `/watchlist/{asteroid_id}` | Update alert thresholds | `{alert_distance_km, alert_cri}` |
| PATCH | `/watchlist/{asteroid_id}/note` | Add custom note | `{note}` |

### **5.4 Alert Endpoints**

| Method | Endpoint | Purpose | Query Params |
|--------|----------|---------|--------------|
| GET | `/alerts` | Get user alerts | `unread_only=true&limit=50` |
| PATCH | `/alerts/{alert_id}/read` | Mark alert as read | - |
| DELETE | `/alerts/{alert_id}` | Delete alert | - |
| GET | `/alerts/stats` | Alert statistics | `days=7` |

### **5.5 User Profile Endpoints**

| Method | Endpoint | Purpose | Payload |
|--------|----------|---------|---------|
| GET | `/user/profile` | Get profile info | - |
| PUT | `/user/profile` | Update profile | `{username, bio, avatar_url}` |
| PUT | `/user/preferences` | Update alert preferences | `{theme, notification_frequency, risk_threshold}` |
| POST | `/user/export` | Export watchlist as CSV | - |

### **5.6 Analytics Endpoints**

| Method | Endpoint | Purpose | Query Params |
|--------|----------|---------|--------------|
| GET | `/analytics/risk-distribution` | Risk score histogram | `days=30` |
| GET | `/analytics/top-threats` | Most dangerous asteroids | `limit=10` |
| GET | `/analytics/user-activity` | User engagement metrics | - |

---

## **6. Frontend Component Structure**

### **6.1 Page-Level Components**

```
pages/
├── Dashboard.tsx          // Main mission control panel
├── AsteroidDetail.tsx    // Single asteroid deep dive
├── Watchlist.tsx         // User's bookmarked asteroids
├── Alerts.tsx            // Notification center
├── Analytics.tsx         // Risk trends & insights
├── Settings.tsx          // User preferences
├── Auth/
│   ├── Login.tsx
│   ├── Register.tsx
│   └── ForgotPassword.tsx
└── NotFound.tsx          // 404 fallback
```

### **6.2 Feature Components**

```
components/
├── Header/
│   ├── Navigation.tsx    // Top nav with logo, user menu
│   ├── SearchBar.tsx     // Global asteroid search
│   └── UserMenu.tsx      // Profile dropdown
├── Dashboard/
│   ├── ThreatCard.tsx    // Next 72h threats widget
│   ├── RiskMeter.tsx     // Animated CRI progress ring
│   ├── AsteroidGrid.tsx  // Paginated asteroid cards
│   ├── AlertBanner.tsx   // High-priority notifications
│   └── StatsSummary.tsx  // Key metrics overview
├── AsteroidDetail/
│   ├── Header.tsx        // Asteroid name + CRI score
│   ├── RiskBreakdown.tsx // Visual risk formula explanation
│   ├── PhysicalProperties.tsx // Size, speed, hazard status
│   ├── ApproachTimeline.tsx   // Past & future approaches
│   ├── WatchlistButton.tsx    // Add to watchlist toggle
│   └── OrbitViz.tsx      // 3D orbit visualization (Three.js)
├── Watchlist/
│   ├── WatchlistTable.tsx    // List view with sort/filter
│   ├── WatchlistCard.tsx     // Card rendition
│   └── ThresholdEditor.tsx   // Set custom alerts
├── Alerts/
│   ├── AlertList.tsx         // Scrollable alert feed
│   ├── AlertCard.tsx         // Individual alert widget
│   └── FilterBar.tsx         // Filter by type, read status
└── Common/
    ├── GlassCard.tsx         // Reusable glassmorphic card
    ├── NeonBadge.tsx         // Risk-colored badge
    ├── LoadingSpinner.tsx    // Animated loading state
    ├── Modal.tsx             // Generic dialog
    └── Toast.tsx             // Notification system
```

### **6.3 Hooks (Custom React Hooks)**

```
hooks/
├── useAsteroids.ts      // Fetch & cache asteroids
├── useWatchlist.ts      // Watchlist CRUD operations
├── useAlerts.ts         // Alert management
├── useCRI.ts            // Risk score calculations
├── useAuth.ts           // Authentication logic
└── useSocket.ts         // WebSocket connection management
```

### **6.4 Utilities**

```
utils/
├── api.ts               // Axios instance with JWT interceptor
├── riskCalculator.ts    // CRI algorithm implementation
├── formatters.ts        // Date, number, distance formatting
├── dateHelpers.ts       // Relative time calculations
└── validators.ts        // Input validation
```

---

## **7. UI/UX Design System**

### **Color Palette (Dark Mode + Neon)**

```
Primary: #0A0E27 (Deep space black)
Secondary: #1A1F3A (Dark navy)
Accent: #00FFE0 (Cyan neon)
Warning: #FF6B35 (Warm orange)
Danger: #FF1744 (Neon red)
Success: #00D084 (Neon green)

Glassmorphism:
- Background: rgba(10, 14, 39, 0.7)
- Border: rgba(0, 255, 224, 0.1)
- Backdrop: blur(10px)
```

### **Typography**
- **Headlines**: Inter Bold, 28-40px (space mission style)
- **Body**: Inter Regular, 14-16px
- **Mono**: JetBrains Mono, 12px (technical info)
- **Spacing Scale**: 4px, 8px, 16px, 24px, 32px (4 × multiplier)

### **Key UI Patterns**

1. **Mission Control Panel Layout**
   - Fixed sidebar with navigation
   - Main content area with animated modules
   - Floating action buttons for quick actions
   - Top warning banner for critical threats

2. **Risk Meter Animation**
   - Circular progress ring (SVG)
   - Color changes from green→yellow→red based on CRI
   - Animated counter (0-100) on hover
   - Tooltip showing risk interpretation

3. **Asteroid Card Hover Effects**
   - Lift (transform: translateY(-4px))
   - Glow (box-shadow: 0 0 30px rgba(0,255,224,0.5))
   - Border highlight
   - Content expansion

4. **Timeline Visualization**
   - Vertical approach history
   - Highlight upcoming close approach
   - Distance to Earth animated scale indicator

---

## **8. Security Architecture**

### **Authentication Flow**
1. User registers → Password hashed with bcrypt (rounds=12)
2. Login returns access_token (15min) + refresh_token (7days)
3. Access token signed with RS256 (asymmetric)
4. Refresh token stored in HttpOnly cookie
5. API validates JWT on every protected endpoint
6. Token refresh chain: client → GET /auth/refresh → new access_token

### **Data Protection**
- All API traffic over HTTPS/TLS
- CORS restricted to frontend domain
- Rate limiting: 100 requests/min per IP
- SQL injection prevention via SQLAlchemy ORM
- XSS protection via Content Security Policy (CSP) headers

### **Best Practices**
- Passwords: bcrypt hash, never stored plaintext
- Secrets: Stored in .env files (not committed)
- API Key (NASA): Managed server-side only
- CSRF tokens for form submissions

---

## **9. NASA API Integration Strategy**

### **Caching Layer**
- **Frequency**: Sync every 6 hours (or on-demand with backoff)
- **Strategy**: Lazy-load close approaches, cache full asteroid list
- **TTL**: 6 hours for asteroid data, 3 hours for approach data
- **Fallback**: Serve last-cached data if API fails

### **Rate Limiting**
- NASA NeoWs free tier: 1000 req/hour
- Implement token bucket: 10 req/sec (safe buffer)
- Batch requests: Fetch 20 asteroids per call, not individual IDs

### **Data Flow**
1. Frontend requests `/neo/feed` → API checks cache
2. If cache miss or stale → Call NASA API asynchronously
3. Store results in PostgreSQL + Redis
4. Return cached data immediately (fast response)
5. Background job updates cache silently

---

## **10. Deployment Strategy**

### **Docker Compose Services**

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| **frontend** | node:18-alpine | 3000 | React dev server or Nginx |
| **backend** | python:3.10-slim | 8000 | FastAPI app |
| **db** | postgres:14-alpine | 5432 | Main database |
| **redis** | redis:7-alpine | 6379 | Cache layer |
| **nginx** | nginx:alpine | 80, 443 | Reverse proxy |

### **Environment Configuration**
- `.env.development` - Local dev with localhost URLs
- `.env.staging` - Staging server URLs
- `.env.production` - Production secrets (injected at deploy time)

### **Volumes**
- `db-data` - PostgreSQL persistent storage
- `backend-logs` - Application logs mounted from host

---

## **11. Performance Optimization**

1. **Frontend**
   - Code-split by route (React.lazy)
   - Image lazy-loading for asteroid thumbnails
   - Service Worker for offline caching
   - Virtual scrolling for large asteroid lists

2. **Backend**
   - Database indexes on: `asteroid_id`, `user_id`, `closest_approach_date`
   - Redis caching with invalidation strategy
   - Pagination: Default 20 items/page
   - Async NASA API calls (non-blocking)

3. **Database**
   - Connection pooling (10-50 connections)
   - Query optimization: Use joins for n+1 fixes
   - Denormalization for risk_score (stored pre-calculated)

---

## **12. Testing Strategy**

- **Backend**: pytest with fixtures for DB mocking
- **Frontend**: Jest + React Testing Library
- **Integration**: Postman automated test collections
- **Load Testing**: k6 for API stress testing

---

## **13. Success Metrics (Hackathon Judging)**

✅ **Core Value**: Unique CRI algorithm (proprietary + explainable)
✅ **Visual Appeal**: Glassmorphism + space-themed UI (memorable)
✅ **Real Data**: Live NASA API integration (not dummy data)
✅ **Completeness**: End-to-end (auth → risk → alerts)
✅ **Scalability**: Docker containerization (production-ready)
✅ **UX**: Intuitive dashboard (judges impressed by mission-control feel)
✅ **Documentation**: Clear API + AI-LOG.md explaining design decisions

---

## **Next Steps**

1. Backend implementation (FastAPI + SQLAlchemy)
2. Frontend scaffold (React + Tailwind)
3. Database schema migration
4. Docker compose development environment
5. API integration testing
6. UI implementation (glassmorphism cards, animations)
7. Advanced features (3D orbit visualization, alerts)
8. Final documentation & deployment guide
