# User API Routes

## Base Path: `/api/users`

### Create User
- **POST** `/api/users`
- **Request Body**:
```json
{
  "username": "john.doe",
  "email": "john.doe@company.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role_ids": ["role-123", "role-456"]
}
```
- **Response**:
```json
{
  "id": "user-789",
  "username": "john.doe",
  "email": "john.doe@company.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": false,
  "role_ids": ["role-123", "role-456"],
  "meta": {"state": "pending"}
}
```

### Get User
- **GET** `/api/users/{id}`
- **Response**: User object with current state

### Update User
- **PUT** `/api/users/{id}`
- **Request Body**: User fields to update + optional transition
```json
{
  "first_name": "John Updated",
  "transition": "activate_user"
}
```

### List Users
- **GET** `/api/users`
- **Query Parameters**: `page`, `limit`, `state`, `role_id`
- **Response**: Paginated list of users

### Delete User
- **DELETE** `/api/users/{id}`

### User Transitions
- **POST** `/api/users/{id}/transitions`
- **Request Body**:
```json
{
  "transition": "activate_user"
}
```
