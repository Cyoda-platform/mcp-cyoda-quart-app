# Routes

## EggAlarmRoutes

### POST /api/egg-alarms
**Description**: Create a new egg alarm
**Transition**: null (entity creation)

**Request Body**:
```json
{
  "userId": "user123",
  "eggType": "SOFT_BOILED",
  "title": "Morning Eggs"
}
```

**Response**:
```json
{
  "id": "alarm456",
  "userId": "user123",
  "eggType": "SOFT_BOILED",
  "duration": 180,
  "title": "Morning Eggs",
  "state": "CREATED",
  "isActive": false,
  "createdAt": "2024-01-15T08:00:00Z",
  "scheduledTime": "2024-01-15T08:03:00Z"
}
```

### GET /api/egg-alarms/{id}
**Description**: Get egg alarm by ID
**Transition**: null

**Response**:
```json
{
  "id": "alarm456",
  "userId": "user123",
  "eggType": "SOFT_BOILED",
  "duration": 180,
  "title": "Morning Eggs",
  "state": "CREATED",
  "isActive": false,
  "createdAt": "2024-01-15T08:00:00Z",
  "scheduledTime": "2024-01-15T08:03:00Z"
}
```

### GET /api/egg-alarms
**Description**: Get all egg alarms for a user
**Query Parameters**: userId (required)
**Transition**: null

**Request Example**: `GET /api/egg-alarms?userId=user123`

**Response**:
```json
{
  "alarms": [
    {
      "id": "alarm456",
      "eggType": "SOFT_BOILED",
      "state": "ACTIVE",
      "isActive": true,
      "scheduledTime": "2024-01-15T08:03:00Z"
    }
  ]
}
```

### PUT /api/egg-alarms/{id}
**Description**: Update egg alarm and optionally transition to new state
**Transition**: Specified in transitionName parameter

**Request Body**:
```json
{
  "transitionName": "CREATED_TO_ACTIVE",
  "title": "Updated Morning Eggs"
}
```

**Response**:
```json
{
  "id": "alarm456",
  "state": "ACTIVE",
  "isActive": true,
  "title": "Updated Morning Eggs"
}
```

### POST /api/egg-alarms/{id}/start
**Description**: Start/activate an egg alarm
**Transition**: CREATED_TO_ACTIVE

**Request Body**:
```json
{
  "transitionName": "CREATED_TO_ACTIVE"
}
```

**Response**:
```json
{
  "id": "alarm456",
  "state": "ACTIVE",
  "isActive": true,
  "scheduledTime": "2024-01-15T08:03:00Z"
}
```

### POST /api/egg-alarms/{id}/cancel
**Description**: Cancel an egg alarm
**Transition**: CREATED_TO_CANCELLED or ACTIVE_TO_CANCELLED

**Request Body**:
```json
{
  "transitionName": "ACTIVE_TO_CANCELLED"
}
```

**Response**:
```json
{
  "id": "alarm456",
  "state": "CANCELLED",
  "isActive": false
}
```

### POST /api/egg-alarms/{id}/reset
**Description**: Reset a completed alarm to create a new one
**Transition**: COMPLETED_TO_CREATED

**Request Body**:
```json
{
  "transitionName": "COMPLETED_TO_CREATED"
}
```

**Response**:
```json
{
  "id": "alarm789",
  "state": "CREATED",
  "isActive": false,
  "eggType": "SOFT_BOILED"
}
```

### DELETE /api/egg-alarms/{id}
**Description**: Delete an egg alarm
**Transition**: null

**Response**:
```json
{
  "message": "Alarm deleted successfully"
}
```

## UserRoutes

### POST /api/users
**Description**: Register a new user
**Transition**: null (entity creation)

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "preferences": {
    "defaultEggType": "MEDIUM_BOILED",
    "notificationSound": "classic"
  }
}
```

**Response**:
```json
{
  "id": "user123",
  "username": "johndoe",
  "email": "john@example.com",
  "state": "REGISTERED",
  "createdAt": "2024-01-15T08:00:00Z"
}
```

### GET /api/users/{id}
**Description**: Get user by ID
**Transition**: null

**Response**:
```json
{
  "id": "user123",
  "username": "johndoe",
  "email": "john@example.com",
  "state": "ACTIVE",
  "createdAt": "2024-01-15T08:00:00Z"
}
```

### PUT /api/users/{id}
**Description**: Update user and optionally transition to new state
**Transition**: Specified in transitionName parameter

**Request Body**:
```json
{
  "transitionName": "REGISTERED_TO_ACTIVE",
  "preferences": {
    "defaultEggType": "HARD_BOILED"
  }
}
```

**Response**:
```json
{
  "id": "user123",
  "state": "ACTIVE",
  "preferences": {
    "defaultEggType": "HARD_BOILED"
  }
}
```

### POST /api/users/{id}/activate
**Description**: Activate a registered user
**Transition**: REGISTERED_TO_ACTIVE

**Request Body**:
```json
{
  "transitionName": "REGISTERED_TO_ACTIVE",
  "verificationToken": "abc123"
}
```

**Response**:
```json
{
  "id": "user123",
  "state": "ACTIVE",
  "message": "User activated successfully"
}
```

### POST /api/users/{id}/suspend
**Description**: Suspend an active user
**Transition**: ACTIVE_TO_SUSPENDED

**Request Body**:
```json
{
  "transitionName": "ACTIVE_TO_SUSPENDED",
  "reason": "Policy violation"
}
```

**Response**:
```json
{
  "id": "user123",
  "state": "SUSPENDED",
  "message": "User suspended successfully"
}
```

### POST /api/users/{id}/reactivate
**Description**: Reactivate a suspended user
**Transition**: SUSPENDED_TO_ACTIVE

**Request Body**:
```json
{
  "transitionName": "SUSPENDED_TO_ACTIVE"
}
```

**Response**:
```json
{
  "id": "user123",
  "state": "ACTIVE",
  "message": "User reactivated successfully"
}
```

### DELETE /api/users/{id}
**Description**: Delete a user account
**Transition**: ACTIVE_TO_DELETED or SUSPENDED_TO_DELETED

**Request Body**:
```json
{
  "transitionName": "ACTIVE_TO_DELETED"
}
```

**Response**:
```json
{
  "message": "User account marked for deletion"
}
```
