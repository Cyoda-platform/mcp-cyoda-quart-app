# User API Routes

## Base Path: `/api/users`

### 1. Create User
- **Method**: POST
- **Path**: `/api/users`
- **Request Body**:
```json
{
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "password": "securepassword123",
  "preferences": {
    "petTypes": ["dogs", "cats"],
    "notifications": true
  }
}
```
- **Response**:
```json
{
  "id": "user-456",
  "status": "success",
  "message": "User created successfully"
}
```

### 2. Get User by ID
- **Method**: GET
- **Path**: `/api/users/{userId}`
- **Response**:
```json
{
  "id": "user-456",
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "state": "registered",
  "preferences": {
    "petTypes": ["dogs", "cats"],
    "notifications": true
  }
}
```

### 3. Update User
- **Method**: PUT
- **Path**: `/api/users/{userId}`
- **Query Parameters**: `transition` (optional) - transition name for state change
- **Request Body**:
```json
{
  "firstName": "Johnny",
  "phone": "+1234567891",
  "transition": "verify_email"
}
```
- **Response**:
```json
{
  "id": "user-456",
  "status": "success",
  "message": "User updated and transitioned to active"
}
```

### 4. Delete User
- **Method**: DELETE
- **Path**: `/api/users/{userId}`
- **Response**:
```json
{
  "status": "success",
  "message": "User deleted successfully"
}
```

### 5. List Users
- **Method**: GET
- **Path**: `/api/users`
- **Query Parameters**: `status`, `limit`, `offset`
- **Response**:
```json
{
  "users": [...],
  "total": 50,
  "limit": 10,
  "offset": 0
}
```
