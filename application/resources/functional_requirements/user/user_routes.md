# User Routes

## Base Path: `/api/users`

## Endpoints

### POST /api/users
Create new user account
- **Transition**: register_user
- **Request**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "timezone": "America/Toronto",
  "notification_time": "08:00"
}
```
- **Response**:
```json
{
  "id": "user-123",
  "email": "user@example.com",
  "name": "John Doe",
  "timezone": "America/Toronto",
  "notification_time": "08:00",
  "active": false,
  "state": "registered"
}
```

### PUT /api/users/{id}
Update user account
- **Transition**: activate_user, suspend_user, reactivate_user, delete_user
- **Request**:
```json
{
  "transition": "activate_user",
  "name": "John Smith",
  "timezone": "America/Vancouver",
  "notification_time": "07:30"
}
```
- **Response**:
```json
{
  "id": "user-123",
  "email": "user@example.com",
  "name": "John Smith",
  "timezone": "America/Vancouver",
  "notification_time": "07:30",
  "active": true,
  "state": "active"
}
```

### GET /api/users/{id}
Get user details
- **Response**:
```json
{
  "id": "user-123",
  "email": "user@example.com",
  "name": "John Doe",
  "timezone": "America/Toronto",
  "notification_time": "08:00",
  "active": true,
  "state": "active"
}
```
