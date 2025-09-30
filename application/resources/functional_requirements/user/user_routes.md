# User API Routes

## Base Path: `/api/users`

### GET /api/users
Get all users
**Response**: Array of user objects

### GET /api/users/{id}
Get user by ID
**Response**: User object

### POST /api/users
Create new user
**Request**:
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "Anytown",
  "zipCode": "12345",
  "dateOfBirth": "1990-01-01",
  "preferredPetType": "dog",
  "experienceLevel": "intermediate",
  "livingSpace": "house"
}
```
**Response**: User ID

### PUT /api/users/{id}
Update user with optional transition
**Request**:
```json
{
  "email": "john.updated@example.com",
  "transition": "verify_user"
}
```
**Response**: Updated user object

### DELETE /api/users/{id}
Delete user
**Response**: Success confirmation
