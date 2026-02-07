# Cosmic Watch - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints (except `/auth/*`) require JWT Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register User
**POST** `/auth/register`

Request:
```json
{
  "email": "user@example.com",
  "username": "astronomer",
  "password": "SecurePassword123"
}
```

Response (201):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Login
**POST** `/auth/login`

Request:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response (200):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Refresh Token
**POST** `/auth/refresh`

Request:
```json
{
  "refresh_token": "eyJhbGc..."
}
```

Response (200):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Get Current User Profile
**GET** `/auth/me`

Response (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "astronomer",
  "preferences": {
    "theme": "dark",
    "notification_frequency": "daily",
    "risk_threshold": 30
  },
  "created_at": "2024-02-07T10:00:00Z",
  "is_active": true
}
```

### Logout
**POST** `/auth/logout`

Response (200):
```json
{
  "message": "Logged out successfully. Please discard token client-side."
}
```

---

## NEO Feed Endpoints

### Get Asteroid Feed
**GET** `/neo/feed?page=1&limit=20&sort=risk_desc`

Query Parameters:
- `page` (int, optional, default=1): Page number
- `limit` (int, optional, default=20): Items per page
- `sort` (string, optional): `risk_desc`, `risk_asc`, `date_asc`, `date_desc`

Response (200):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "neo_id": "3122270",
      "name": "Apophis",
      "diameter_km": 0.37,
      "is_hazardous": true,
      "cri_score": 75.5,
      "risk_level": {
        "level": "RED",
        "emoji": "⚠️",
        "color": "#FF6B35",
        "description": "Very close approach - Significant risk",
        "recommendation": "Add to watchlist for continuous monitoring"
      }
    }
  ],
  "total_count": 28034,
  "page": 1,
  "page_size": 20,
  "total_pages": 1402
}
```

### Get Next 72 Hours Threats
**GET** `/neo/next-72h?threat_level=high`

Query Parameters:
- `threat_level` (string, optional): `critical`, `high`, `medium`, `low`

Response (200):
```json
{
  "threats": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "neo_id": "3122270",
      "name": "Apophis",
      "diameter_km": 0.37,
      "is_hazardous": true,
      "cri_score": 75.5,
      "next_approach": {
        "closest_approach_date": "2024-02-15T10:30:00Z",
        "miss_distance_km": 2500000,
        "approach_velocity_kmh": 45000,
        "calculated_cri": 75.5,
        "is_next_72h_threat": true,
        "days_until_approach": 8
      }
    }
  ],
  "total_count": 12,
  "highest_cri": 92.3,
  "critical_count": 3
}
```

### Get Asteroid Detail
**GET** `/neo/{asteroid_id}`

Response (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "neo_id": "3122270",
  "name": "Apophis",
  "url": "https://cneos.jpl.nasa.gov/...",
  "diameter_km": 0.37,
  "diameter_min_km": 0.34,
  "diameter_max_km": 0.41,
  "absolute_magnitude": 19.2,
  "is_hazardous": true,
  "is_sentry_object": false,
  "next_approach": {
    "closest_approach_date": "2024-02-15T10:30:00Z",
    "miss_distance_km": 2500000,
    "approach_velocity_kmh": 45000,
    "calculated_cri": 75.5,
    "is_next_72h_threat": false,
    "days_until_approach": 8
  },
  "cri_score": 75.5,
  "risk_level": {
    "level": "RED",
    "emoji": "⚠️",
    "color": "#FF6B35",
    "description": "Very close approach - Significant risk"
  },
  "cri_components": {
    "diameter_score": 35.2,
    "velocity_score": 72.5,
    "distance_score": 68.3,
    "hazard_bonus": 15.0,
    "final_cri": 75.5
  },
  "all_approaches": [
    {
      "closest_approach_date": "2024-02-15T10:30:00Z",
      "miss_distance_km": 2500000,
      "approach_velocity_kmh": 45000,
      "calculated_cri": 75.5
    }
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "nasa_synced_at": "2024-02-07T10:00:00Z"
}
```

### Search Asteroids
**GET** `/neo/search?q=Apophis&limit=10`

Query Parameters:
- `q` (string, required): Search query
- `limit` (int, optional, default=10): Max results

Response (200):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "neo_id": "3122270",
    "name": "Apophis",
    ...
  }
]
```

### Get Today's Asteroids
**GET** `/neo/today`

Response (200):
```json
{
  "count": 5,
  "asteroids": [...]
}
```

---

## Watchlist Endpoints

### Get User Watchlist
**GET** `/watchlist`

Response (200):
```json
{
  "items": [
    {
      "id": "650e8400-e29b-41d4-a716-446655440000",
      "asteroid": {...},
      "alert_threshold_distance_km": 5000000,
      "alert_threshold_cri": 50,
      "custom_notes": "Close approach in Q2 2024",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total_count": 1
}
```

### Add to Watchlist
**POST** `/watchlist`

Request:
```json
{
  "asteroid_id": "550e8400-e29b-41d4-a716-446655440000",
  "alert_threshold_distance_km": 5000000,
  "alert_threshold_cri": 50
}
```

Response (200):
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440000",
  "asteroid": {...},
  "alert_threshold_distance_km": 5000000,
  "alert_threshold_cri": 50,
  "custom_notes": null,
  "created_at": "2024-02-07T10:00:00Z"
}
```

### Update Watchlist Item
**PUT** `/watchlist/{asteroid_id}`

Request:
```json
{
  "alert_threshold_distance_km": 3000000,
  "alert_threshold_cri": 60,
  "custom_notes": "Updated observation notes"
}
```

Response (200):
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440000",
  "asteroid": {...},
  "alert_threshold_distance_km": 3000000,
  "alert_threshold_cri": 60,
  "custom_notes": "Updated observation notes",
  "created_at": "2024-02-07T10:00:00Z"
}
```

### Remove from Watchlist
**DELETE** `/watchlist/{asteroid_id}`

Response (200):
```json
{"success": true, "message": "Removed from watchlist"}
```

### Check Watchlist Status
**GET** `/watchlist/{asteroid_id}/status`

Response (200):
```json
{"in_watchlist": true}
```

---

## Alert Endpoints

### Get Alerts
**GET** `/alerts?unread_only=false&limit=50&offset=0`

Query Parameters:
- `unread_only` (boolean, optional): Only unread alerts
- `limit` (int, optional): Items per page
- `offset` (int, optional): Pagination offset

Response (200):
```json
{
  "items": [
    {
      "id": "750e8400-e29b-41d4-a716-446655440000",
      "asteroid_id": "550e8400-e29b-41d4-a716-446655440000",
      "asteroid_name": "Apophis",
      "alert_type": "DISTANCE",
      "triggered_reason": "Asteroid within 5000000 km threshold",
      "cri_score_at_trigger": 75.5,
      "distance_at_trigger_km": 4800000,
      "is_read": false,
      "triggered_at": "2024-02-07T10:00:00Z"
    }
  ],
  "total_count": 3,
  "unread_count": 1
}
```

### Mark Alert as Read
**PATCH** `/alerts/{alert_id}/read`

Response (200):
```json
{"success": true, "message": "Alert marked as read"}
```

### Delete Alert
**DELETE** `/alerts/{alert_id}`

Response (200):
```json
{"success": true, "message": "Alert deleted"}
```

### Get Alert Statistics
**GET** `/alerts/stats?days=7`

Query Parameters:
- `days` (int, optional, default=7): Number of days to analyze

Response (200):
```json
{
  "total_alerts": 15,
  "unread_alerts": 2,
  "critical_alerts": 3,
  "high_alerts": 5,
  "medium_alerts": 7,
  "alerts_by_type": {
    "DISTANCE": 8,
    "RISK_SCORE": 5,
    "APPROACH_24H": 2
  }
}
```

### Check Watchlist Thresholds
**POST** `/alerts/check-thresholds`

Response (200):
```json
{
  "success": true,
  "alerts_triggered": 2,
  "message": "Triggered 2 new alerts based on watchlist thresholds"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-02-07T10:00:00Z"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials",
  "error_code": "AUTH_ERROR",
  "timestamp": "2024-02-07T10:00:00Z"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found",
  "error_code": "NOT_FOUND",
  "timestamp": "2024-02-07T10:00:00Z"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "timestamp": "2024-02-07T10:00:00Z"
}
```

---

## Rate Limiting

- **Default limit**: 100 requests per minute per IP
- **NASA API**: 10 requests per second (cached responses)
- **Rate limit headers**:
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

### Get Feed (with token)
```bash
curl -X GET http://localhost:8000/neo/feed \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Postman Collection

Import the Postman collection from `docs/cosmic-watch-api.postman_collection.json` to test all endpoints interactively.
