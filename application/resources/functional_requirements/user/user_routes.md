# User API Routes

## Base Route: `/api/users`

### Endpoints:

**POST /api/users** - Create new user
- **Request**: `{"username": "john_doe", "firstName": "John", "lastName": "Doe", "email": "john@example.com", "password": "password123", "phone": "+1234567890", "userStatus": 0}`
- **Response**: `{"id": "789", "username": "john_doe", "firstName": "John", "lastName": "Doe", "email": "john@example.com", "phone": "+1234567890", "userStatus": 0}`

**GET /api/users/{username}** - Get user by username
- **Response**: `{"id": "789", "username": "john_doe", "firstName": "John", "lastName": "Doe", "email": "john@example.com", "phone": "+1234567890", "userStatus": 1}`

**PUT /api/users/{username}** - Update user with optional transition
- **Request**: `{"firstName": "Johnny", "userStatus": 1, "transition": "activate_user"}`
- **Response**: `{"id": "789", "username": "john_doe", "firstName": "Johnny", "userStatus": 1}`

**DELETE /api/users/{username}** - Delete user
- **Response**: `{"message": "User deleted successfully"}`

**GET /api/users/login?username=john_doe&password=password123** - User login
- **Response**: `{"token": "auth_token_here", "expires": "2024-01-15T10:00:00Z"}`
