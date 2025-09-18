# User Routes

## Description
REST API endpoints for managing users in the Purrfect Pets store.

## Endpoints

### GET /users
Get all users.

**Request Example:**
```
GET /users
```

**Response Example:**
```json
[
  {
    "id": "user-123",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "address": "123 Main St, City, State",
    "meta": {"state": "active"}
  }
]
```

### GET /users/{id}
Get a specific user by ID.

**Request Example:**
```
GET /users/user-123
```

**Response Example:**
```json
{
  "id": "user-123",
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St, City, State",
  "meta": {"state": "active"}
}
```

### POST /users
Create a new user.

**Request Example:**
```json
{
  "username": "jane_smith",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "+1987654321",
  "address": "456 Oak Ave, City, State"
}
```

**Response Example:**
```json
{
  "id": "user-124"
}
```

### PUT /users/{id}
Update a user with optional transition.

**Request Example:**
```json
{
  "username": "jane_smith_updated",
  "first_name": "Jane",
  "last_name": "Smith-Johnson",
  "email": "jane.johnson@example.com",
  "phone": "+1987654321",
  "address": "789 Pine St, City, State",
  "transition": "activate_user"
}
```

**Response Example:**
```json
{
  "success": true
}
```

### DELETE /users/{id}
Delete a user.

**Request Example:**
```
DELETE /users/user-123
```

**Response Example:**
```json
{
  "success": true
}
```
