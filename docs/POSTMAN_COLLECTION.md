# Cosmic Watch - Postman Collection Structure

## Collection: Cosmic Watch API

### Pre-request Script (Auth Token Management)
```javascript
// Auto-load token from saved response
const savedToken = pm.environment.get("access_token");
if (savedToken) {
    pm.request.headers.add({Key: 'Authorization', Value: 'Bearer ' + savedToken});
}
```

---

## Folder: Auth Endpoints

### 1. Register User
**POST** `/auth/register`
```json
{
  "email": "test@cosmic-watch.io",
  "username": "astronomer_1",
  "password": "SecurePassword123!"
}
```
**Tests:**
- Response status 200
- Extract access_token
- Extract refresh_token

### 2. Login
**POST** `/auth/login`
```json
{
  "email": "test@cosmic-watch.io",
  "password": "SecurePassword123!"
}
```
**Tests:**
- Response status 200
- Save access_token to environment
- Verify token_type = "bearer"

### 3. Get Current User
**GET** `/auth/me`
**Headers:** Authorization: Bearer {{access_token}}

**Tests:**
- Response status 200
- Verify email matches login

### 4. Refresh Token
**POST** `/auth/refresh`
```json
{
  "refresh_token": "{{refresh_token}}"
}
```
**Tests:**
- Response status 200
- Token should be different from previous

---

## Folder: NEO Feed Endpoints

### 1. Get Asteroid Feed
**GET** `/neo/feed?page=1&limit=20&sort=risk_desc`
**Headers:** Authorization: Bearer {{access_token}}

**Test Cases:**
- Verify paginated response
- Check CRI score present
- Verify asteroids sorted by risk

### 2. Get Next 72h Threats
**GET** `/neo/next-72h?threat_level=high`
**Headers:** Authorization: Bearer {{access_token}}

**Test Cases:**
- Response contains threat array
- All CRI scores >= 40
- Verify threat_count > 0

### 3. Get Asteroid Detail
**GET** `/neo/{{asteroid_id}}`
**Headers:** Authorization: Bearer {{access_token}}

**Test Cases:**
- Response has all physical properties
- Risk level is populated
- CRI components breakdown present

### 4. Search Asteroids
**GET** `/neo/search?q=Apophis&limit=10`
**Headers:** Authorization: Bearer {{access_token}}

**Test Cases:**
- Results contain search term
- Max 10 results returned

### 5. Get Today's Asteroids
**GET** `/neo/today`
**Headers:** Authorization: Bearer {{access_token}}

---

## Folder: Watchlist Management

### 1. Get Watchlist
**GET** `/watchlist`
**Headers:** Authorization: Bearer {{access_token}}

**Test Cases:**
- Response is array of watchlisted asteroids
- Each item has asteroid and alert thresholds

### 2. Add to Watchlist
**POST** `/watchlist`
**Headers:** Authorization: Bearer {{access_token}}
```json
{
  "asteroid_id": "550e8400-e29b-41d4-a716-446655440000",
  "alert_threshold_distance_km": 5000000,
  "alert_threshold_cri": 50
}
```
**Tests:**
- Status 200
- Item appears in watchlist

### 3. Update Watchlist Item
**PUT** `/watchlist/{{asteroid_id}}`
```json
{
  "alert_threshold_distance_km": 3000000,
  "alert_threshold_cri": 60,
  "custom_notes": "Close approach in June"
}
```

### 4. Remove from Watchlist
**DELETE** `/watchlist/{{asteroid_id}}`

### 5. Check Watchlist Status
**GET** `/watchlist/{{asteroid_id}}/status`

---

## Folder: Alert System

### 1. Get Alerts
**GET** `/alerts?unread_only=false&limit=50`
**Headers:** Authorization: Bearer {{access_token}}

**Test Cases:**
- Response paginated correctly
- Unread_count >= 0

### 2. Mark Alert as Read
**PATCH** `/alerts/{{alert_id}}/read`

### 3. Delete Alert
**DELETE** `/alerts/{{alert_id}}`

### 4. Get Alert Statistics
**GET** `/alerts/stats?days=7`
**Headers:** Authorization: Bearer {{access_token}}

**Test Cases:**
- Verify alert counts match
- Total = critical + high + medium

### 5. Check Watchlist Thresholds
**POST** `/alerts/check-thresholds`
**Headers:** Authorization: Bearer {{access_token}}

---

## Environment Variables

```javascript
{
  "base_url": "http://localhost:8000",
  "access_token": "{{$RESPONSE_TOKEN}}",
  "refresh_token": "{{$REFRESH_TOKEN}}",
  "asteroid_id": "550e8400-e29b-41d4-a716-446655440000",
  "alert_id": "750e8400-e29b-41d4-a716-446655440000"
}
```

---

## Test Workflow

### 1. Auth Flow
- Register User → Save tokens
- Login → Update tokens
- Get Current User → Verify login
- Refresh Token → Get new access token

### 2. Asteroid Discovery
- Get Feed → Extract first asteroid_id
- Search Asteroids → Specific query
- Get Asteroid Detail → Full details
- Get Next 72h → Critical threats
- Get Today's → Daily approaches

### 3. Watchlist Workflow
- Add to Watchlist → asteroid gets tracked
- Get Watchlist → Verify added
- Update Watchlist → Change thresholds
- Check Status → Confirm in list
- Remove → Delete from list

### 4. Alert Management
- Check Thresholds → Trigger alerts
- Get Alerts → List notifications
- Alert Stats → Verify counts
- Mark Read → Update status
- Delete → Remove alert

---

## Example Test Script

```javascript
// Before Each Request
const token = pm.environment.get("access_token");
if (!token && pm.request.headers.get("Authorization")) {
    console.error("No token found. Please run Login endpoint first.");
}

// After Each Request (Success Case)
if (pm.response.code === 200 || pm.response.code === 201) {
    pm.test("Status OK", function() {
        pm.expect(pm.response.code).to.be.oneOf([200, 201]);
    });
    
    const responseJson = pm.response.json();
    if (responseJson.access_token) {
        pm.environment.set("access_token", responseJson.access_token);
        console.log("✅ Token updated");
    }
}
```

---

## Performance Testing

### Load Test: Get Feed Endpoint
- Requests: 100 concurrent
- Duration: 1 minute
- Expected response time: < 500ms P95

### Stress Test: Watchlist Operations
- Add/remove 50 asteroids rapidly
- Expected consistency: 100%

---

## Security Testing

- [ ] Invalid token rejection
- [ ] CORS headers validation
- [ ] SQL injection prevention (search)
- [ ] Rate limiting (100 req/min)
- [ ] Password strength validation

---

## Import Instructions

1. Open Postman
2. Click Import → Upload this collection
3. Set base_url environment variable
4. Run Auth workflow first
5. Execute other endpoints

**Happy API Testing!** 🛸
