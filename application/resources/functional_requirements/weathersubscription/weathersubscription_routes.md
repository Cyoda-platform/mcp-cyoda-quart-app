# WeatherSubscription Routes

## Base Path: `/api/subscriptions`

## Endpoints

### POST /api/subscriptions
Create new weather subscription
- **Transition**: create_subscription
- **Request**:
```json
{
  "user_id": "user-123",
  "location": "Toronto, ON, Canada",
  "latitude": 43.6532,
  "longitude": -79.3832,
  "frequency": "daily"
}
```
- **Response**:
```json
{
  "id": "sub-456",
  "user_id": "user-123",
  "location": "Toronto, ON, Canada",
  "latitude": 43.6532,
  "longitude": -79.3832,
  "frequency": "daily",
  "active": false,
  "state": "created"
}
```

### PUT /api/subscriptions/{id}
Update subscription
- **Transition**: activate_subscription, pause_subscription, resume_subscription, cancel_subscription
- **Request**:
```json
{
  "transition": "activate_subscription",
  "frequency": "daily"
}
```
- **Response**:
```json
{
  "id": "sub-456",
  "user_id": "user-123",
  "location": "Toronto, ON, Canada",
  "latitude": 43.6532,
  "longitude": -79.3832,
  "frequency": "daily",
  "active": true,
  "state": "active"
}
```

### GET /api/subscriptions/{id}
Get subscription details
- **Response**:
```json
{
  "id": "sub-456",
  "user_id": "user-123",
  "location": "Toronto, ON, Canada",
  "latitude": 43.6532,
  "longitude": -79.3832,
  "frequency": "daily",
  "active": true,
  "state": "active"
}
```

### GET /api/users/{user_id}/subscriptions
Get user's subscriptions
- **Response**:
```json
[
  {
    "id": "sub-456",
    "location": "Toronto, ON, Canada",
    "frequency": "daily",
    "active": true,
    "state": "active"
  }
]
```
