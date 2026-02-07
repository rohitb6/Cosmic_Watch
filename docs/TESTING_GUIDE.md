# Testing Guide - Cosmic Watch

## Overview

This guide covers testing strategies for the Cosmic Watch platform, including unit tests, integration tests, and end-to-end tests.

---

## 🧪 Backend Testing

### Unit Tests Setup

```bash
cd backend

# Install pytest and plugins
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_auth_service.py

# Run specific test function
pytest tests/test_auth_service.py::test_register_user_success
```

### Test Structure

```
backend/tests/
├── conftest.py              # Fixtures and configuration
├── test_auth_service.py     # Authentication tests
├── test_asteroid_service.py # Asteroid service tests
├── test_watchlist_service.py
├── test_alert_service.py
├── test_risk_calculator.py
└── integration/
    ├── test_auth_routes.py
    ├── test_asteroid_routes.py
    └── test_watchlist_routes.py
```

### Example Unit Test

```python
# tests/test_risk_calculator.py
import pytest
from app.utils.risk_calculator import calculate_cri, get_risk_level

@pytest.mark.asyncio
async def test_calculate_cri_safe_asteroid():
    """Test CRI calculation for safe asteroid"""
    cri = calculate_cri(
        diameter=0.5,      # Small diameter
        velocity=15000,    # Normal velocity
        miss_distance=10000000,  # Far away
        is_hazardous=False
    )
    assert 0 <= cri <= 20  # Should be in "Green" range

@pytest.mark.asyncio
async def test_calculate_cri_critical_asteroid():
    """Test CRI calculation for critical hazard"""
    cri = calculate_cri(
        diameter=500,      # Large diameter
        velocity=50000,    # High velocity
        miss_distance=100000,   # Close approach
        is_hazardous=True
    )
    assert cri >= 80  # Should be "Critical" or higher

def test_get_risk_level_mapping():
    """Test risk level to emoji/color mapping"""
    assert get_risk_level(15)["emoji"] == "🟢"  # Green
    assert get_risk_level(35)["emoji"] == "🟡"  # Yellow
    assert get_risk_level(55)["emoji"] == "🟠"  # Orange
    assert get_risk_level(75)["emoji"] == "🔴"  # Red
    assert get_risk_level(95)["emoji"] == "⚫"  # Critical
```

### Test Authentication Service

```python
# tests/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.schemas.schemas import UserRegisterRequest, UserLoginRequest
from app.core.security import verify_password

@pytest.fixture
def user_data():
    return UserRegisterRequest(
        email="test@cosmic-watch.io",
        username="test_astronomer",
        password="SecurePassword123!"
    )

@pytest.mark.asyncio
async def test_register_user_success(db, user_data):
    """Test successful user registration"""
    user = await AuthService.register_user(db, user_data)
    
    assert user.email == user_data.email
    assert user.username == user_data.username
    assert verify_password(user_data.password, user.password_hash)

@pytest.mark.asyncio
async def test_register_user_duplicate_email(db, user_data):
    """Test registering with existing email"""
    await AuthService.register_user(db, user_data)
    
    with pytest.raises(ValueError, match="Email already registered"):
        await AuthService.register_user(db, user_data)

@pytest.mark.asyncio
async def test_login_user_success(db, user_data):
    """Test successful login"""
    await AuthService.register_user(db, user_data)
    
    tokens = await AuthService.login_user(
        db,
        UserLoginRequest(email=user_data.email, password=user_data.password)
    )
    
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user_invalid_password(db, user_data):
    """Test login with wrong password"""
    await AuthService.register_user(db, user_data)
    
    with pytest.raises(ValueError, match="Invalid credentials"):
        await AuthService.login_user(
            db,
            UserLoginRequest(email=user_data.email, password="WrongPassword")
        )
```

### Test Asteroid Service

```python
# tests/test_asteroid_service.py
@pytest.mark.asyncio
async def test_fetch_nasa_asteroids_success(db, mock_nasa_response):
    """Test fetching asteroids from NASA API"""
    asteroids = await AsteroidService.fetch_nasa_asteroids(db)
    
    assert len(asteroids) > 0
    assert all(hasattr(a, 'neo_id') for a in asteroids)

@pytest.mark.asyncio
async def test_search_asteroids_by_name(db, sample_asteroids):
    """Test asteroid search functionality"""
    results = await AsteroidService.search_asteroids(
        db, 
        query="Apophis",
        limit=10
    )
    
    assert any("Apophis" in a.name for a in results)

@pytest.mark.asyncio
async def test_get_asteroid_detail(db, sample_asteroid):
    """Test fetching detailed asteroid information"""
    detail = await AsteroidService.get_asteroid_detail(
        db,
        asteroid_id=sample_asteroid.neo_id
    )
    
    assert detail.neo_id == sample_asteroid.neo_id
    assert "close_approaches" in detail.dict()
```

### Conftest Configuration

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal()
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """Create test client"""
    def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Create authenticated headers"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@test.io",
            "username": "testuser",
            "password": "TestPass123!"
        }
    )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
```

---

## 🧪 Frontend Testing

### Jest Unit Tests

```bash
cd frontend

# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

### Example Component Test

```typescript
// src/components/__tests__/RiskMeter.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import RiskMeter from '../RiskMeter';

describe('RiskMeter Component', () => {
  it('renders with green color for low risk', () => {
    render(<RiskMeter cri={15} />);
    
    const meter = screen.getByTestId('risk-meter');
    expect(meter).toHaveClass('risk-low');
  });

  it('renders with red color for high risk', () => {
    render(<RiskMeter cri={75} />);
    
    const meter = screen.getByTestId('risk-meter');
    expect(meter).toHaveClass('risk-high');
  });

  it('displays correct percentage', () => {
    render(<RiskMeter cri={50} />);
    
    expect(screen.getByText('50%')).toBeInTheDocument();
  });
});
```

### Hook Testing

```typescript
// src/hooks/__tests__/useAsteroids.test.ts
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAsteroids } from '../useAsteroids';

describe('useAsteroids Hook', () => {
  it('fetches asteroids on mount', async () => {
    const { result } = renderHook(() => useAsteroids());
    
    await waitFor(() => {
      expect(result.current.asteroids).toBeDefined();
    });
  });

  it('handles search query', async () => {
    const { result } = renderHook(() => useAsteroids());
    
    act(() => {
      result.current.search('Apophis');
    });
    
    await waitFor(() => {
      expect(result.current.asteroids).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ name: expect.stringContaining('Apophis') })
        ])
      );
    });
  });
});
```

### API Integration Tests

```typescript
// src/__tests__/api.test.ts
import { api } from '../utils/api';

describe('API Client', () => {
  it('includes auth token in requests', async () => {
    localStorage.setItem('access_token', 'test-token-123');
    
    const instance = api();
    expect(instance.defaults.headers.common['Authorization']).toBe('Bearer test-token-123');
  });

  it('handles 401 errors by refreshing token', async () => {
    // Mock implementation
    const response = await api().get('/protected-endpoint');
    // Should auto-refresh and retry
  });
});
```

---

## 🔗 Integration Tests

### API Endpoint Tests

```python
# tests/integration/test_asteroid_routes.py
@pytest.mark.asyncio
async def test_get_feed_endpoint(client, auth_headers):
    """Test GET /neo/feed endpoint"""
    response = client.get(
        "/neo/feed?page=1&limit=20",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "asteroids" in data
    assert "total_count" in data
    assert len(data["asteroids"]) <= 20

@pytest.mark.asyncio
async def test_get_next_72h_endpoint(client, auth_headers):
    """Test GET /neo/next-72h endpoint"""
    response = client.get(
        "/neo/next-72h?threat_level=high",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "threats" in data
    assert all(t["cri"] >= 40 for t in data["threats"])

@pytest.mark.asyncio
async def test_add_watchlist_endpoint(client, auth_headers, sample_asteroid):
    """Test POST /watchlist endpoint"""
    response = client.post(
        "/watchlist",
        headers=auth_headers,
        json={
            "asteroid_id": sample_asteroid.neo_id,
            "alert_threshold_distance_km": 5000000,
            "alert_threshold_cri": 50
        }
    )
    
    assert response.status_code == 200
    
    # Verify it was added
    response = client.get("/watchlist", headers=auth_headers)
    assert sample_asteroid.neo_id in [item["asteroid"]["neo_id"] for item in response.json()]
```

---

## 📊 End-to-End Tests (E2E)

### Cypress Tests

```bash
# Install Cypress
npm install --save-dev cypress

# Open Cypress Test Runner
npx cypress open

# Run tests headless
npx cypress run
```

### Example E2E Test

```javascript
// cypress/e2e/dashboard.cy.js
describe('Dashboard E2E', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000');
    cy.login('test@cosmic-watch.io', 'TestPassword123!');
  });

  it('displays next 72h threats', () => {
    cy.get('[data-cy=threats-section]').should('be.visible');
    cy.get('[data-cy=threat-card]').should('have.length.greaterThan', 0);
  });

  it('allows adding asteroid to watchlist', () => {
    cy.get('[data-cy=threat-card]').first().click();
    cy.get('[data-cy=add-to-watchlist-btn]').click();
    
    cy.get('[data-cy=toast-success]').should('contain', 'Added to watchlist');
    
    cy.visit('http://localhost:3000/watchlist');
    cy.get('[data-cy=watchlist-item]').should('have.length.greaterThan', 0);
  });

  it('allows setting alert thresholds', () => {
    cy.visit('http://localhost:3000/watchlist');
    cy.get('[data-cy=watchlist-item]').first().find('[data-cy=edit-btn]').click();
    
    cy.get('[data-cy=cri-threshold]').clear().type('75');
    cy.get('[data-cy=save-btn]').click();
    
    cy.get('[data-cy=toast-success]').should('contain', 'Updated');
  });
});
```

---

## 🚀 Performance Tests

### Load Testing with K6

```javascript
// load-tests/dashboard.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp-up
    { duration: '1m30s', target: 20 }, // Stay at 20 users
    { duration: '30s', target: 0 },    // Ramp-down
  ],
};

export default function () {
  let token = 'your-test-token';
  
  let response = http.get('http://localhost:8000/neo/feed', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

```bash
# Run load test
k6 run load-tests/dashboard.js
```

---

## ✅ Testing Checklist

### Backend Tests
- [ ] Authentication (register, login, refresh, logout)
- [ ] Asteroid operations (fetch, search, detail, next-72h)
- [ ] Watchlist management (add, remove, update, check)
- [ ] Alert system (trigger, get, read, stats)
- [ ] Risk calculation algorithm
- [ ] Database operations
- [ ] Error handling

### Frontend Tests
- [ ] Component rendering
- [ ] User interactions (clicks, form submissions)
- [ ] API calls with mocking
- [ ] Authentication flow
- [ ] Routing and navigation
- [ ] Responsive design

### Integration Tests
- [ ] Full auth flow (register → login → access protected resource)
- [ ] Watchlist workflow (add → update → remove)
- [ ] Alert triggering on threshold
- [ ] NASA API sync

### E2E Tests
- [ ] User registration and login
- [ ] Dashboard functionality
- [ ] Search and filter operations
- [ ] Watchlist management
- [ ] Alert notifications

---

## 📈 Coverage Goals

| Component | Target Coverage |
|-----------|-----------------|
| Backend Services | 80%+ |
| Database Models | 85%+ |
| API Routes | 80%+ |
| Frontend Components | 70%+ |
| Frontend Hooks | 75%+ |
| Risk Calculator | 95%+ (Critical) |

---

## 🔍 Running All Tests

```bash
# Backend
cd backend
pytest --cov=app --cov-report=term-missing

# Frontend
cd ../frontend
npm test -- --coverage

# E2E
npx cypress run

# All coverage report
npm run test:all:coverage
```

---

## 📚 Testing Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [Cypress Documentation](https://docs.cypress.io/)
- [K6 Load Testing](https://k6.io/docs/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-databases/)

---

**Last Updated**: 2024
**Questions?** Check the respective framework documentation or create an issue
