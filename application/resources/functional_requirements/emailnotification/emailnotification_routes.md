# EmailNotification Routes

## Base Path: `/api/notifications`

## Endpoints

### POST /api/notifications
Create email notification
- **Transition**: create_notification
- **Request**:
```json
{
  "user_id": "user-123",
  "weather_data_id": "weather-789"
}
```
- **Response**:
```json
{
  "id": "notification-101",
  "user_id": "user-123",
  "weather_data_id": "weather-789",
  "recipient_email": "user@example.com",
  "subject": "Daily Weather Update for Toronto, ON - January 15, 2024",
  "delivery_status": "pending",
  "retry_count": 0,
  "state": "pending"
}
```

### PUT /api/notifications/{id}
Update notification status
- **Transition**: send_email, confirm_delivery, mark_failed, retry_send
- **Request**:
```json
{
  "transition": "send_email"
}
```
- **Response**:
```json
{
  "id": "notification-101",
  "user_id": "user-123",
  "weather_data_id": "weather-789",
  "recipient_email": "user@example.com",
  "subject": "Daily Weather Update for Toronto, ON - January 15, 2024",
  "delivery_status": "sending",
  "retry_count": 1,
  "state": "sending"
}
```

### GET /api/notifications/{id}
Get notification details
- **Response**:
```json
{
  "id": "notification-101",
  "user_id": "user-123",
  "weather_data_id": "weather-789",
  "recipient_email": "user@example.com",
  "subject": "Daily Weather Update for Toronto, ON - January 15, 2024",
  "content": "Good Morning! Here's your daily weather update for Toronto, ON...",
  "sent_timestamp": "2024-01-15T08:00:00Z",
  "delivery_status": "sent",
  "retry_count": 1,
  "state": "sent"
}
```

### GET /api/users/{user_id}/notifications
Get user's notifications
- **Response**:
```json
[
  {
    "id": "notification-101",
    "weather_data_id": "weather-789",
    "subject": "Daily Weather Update for Toronto, ON - January 15, 2024",
    "sent_timestamp": "2024-01-15T08:00:00Z",
    "delivery_status": "sent",
    "state": "sent"
  }
]
```
