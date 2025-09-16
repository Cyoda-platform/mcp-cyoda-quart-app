# Routes for Purrfect Pets API

## PetRoutes

### GET /api/pets
**Description:** Get all pets with optional filtering
**Parameters:** 
- category_id (optional): Filter by category
- status (optional): Filter by pet state (Available, Pending, Sold)
- page (optional): Page number (default: 0)
- size (optional): Page size (default: 20)

**Request Example:**
```
GET /api/pets?category_id=1&status=Available&page=0&size=10
```

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "name": "Fluffy",
      "category_id": 1,
      "breed": "Persian",
      "age": 2,
      "price": 500.0,
      "state": "Available"
    }
  ],
  "totalElements": 1,
  "totalPages": 1
}
```

### GET /api/pets/{id}
**Description:** Get pet by ID
**Parameters:** id (path): Pet ID

**Request Example:**
```
GET /api/pets/1
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Fluffy",
  "category_id": 1,
  "photo_urls": ["http://example.com/fluffy1.jpg"],
  "tags": ["cute", "playful"],
  "breed": "Persian",
  "age": 2,
  "weight": 3.5,
  "color": "white",
  "description": "Beautiful Persian cat",
  "price": 500.0,
  "vaccination_status": true,
  "state": "Available",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

### POST /api/pets
**Description:** Create new pet
**Parameters:** transition_name: null (automatic transition to Available)

**Request Example:**
```json
{
  "name": "Buddy",
  "category_id": 2,
  "photo_urls": ["http://example.com/buddy1.jpg"],
  "tags": ["friendly", "energetic"],
  "breed": "Golden Retriever",
  "age": 1,
  "weight": 25.0,
  "color": "golden",
  "description": "Friendly Golden Retriever puppy",
  "price": 800.0,
  "vaccination_status": true
}
```

**Response Example:**
```json
{
  "id": 2,
  "name": "Buddy",
  "state": "Available",
  "created_at": "2024-01-01T11:00:00"
}
```

### PUT /api/pets/{id}
**Description:** Update pet
**Parameters:** 
- id (path): Pet ID
- transition_name (optional): Transition name for state change

**Request Example:**
```json
{
  "name": "Buddy Updated",
  "description": "Updated description",
  "price": 850.0,
  "transition_name": null
}
```

### PUT /api/pets/{id}/reserve
**Description:** Reserve pet for order
**Parameters:** 
- id (path): Pet ID
- transition_name: "PetReservation"

**Request Example:**
```json
{
  "order_id": 1,
  "transition_name": "PetReservation"
}
```

### PUT /api/pets/{id}/release
**Description:** Release pet reservation
**Parameters:** 
- id (path): Pet ID
- transition_name: "PetRelease"

**Request Example:**
```json
{
  "order_id": 1,
  "reason": "Order cancelled",
  "transition_name": "PetRelease"
}
```

### DELETE /api/pets/{id}
**Description:** Delete pet (soft delete)

---

## CategoryRoutes

### GET /api/categories
**Description:** Get all categories

**Request Example:**
```
GET /api/categories
```

**Response Example:**
```json
[
  {
    "id": 1,
    "name": "Cats",
    "description": "Feline companions",
    "state": "Active"
  },
  {
    "id": 2,
    "name": "Dogs",
    "description": "Canine companions",
    "state": "Active"
  }
]
```

### GET /api/categories/{id}
**Description:** Get category by ID

### POST /api/categories
**Description:** Create new category
**Parameters:** transition_name: null (automatic transition to Active)

**Request Example:**
```json
{
  "name": "Birds",
  "description": "Feathered friends"
}
```

### PUT /api/categories/{id}
**Description:** Update category
**Parameters:** transition_name (optional): For state changes

### PUT /api/categories/{id}/deactivate
**Description:** Deactivate category
**Parameters:** transition_name: "CategoryDeactivation"

**Request Example:**
```json
{
  "transition_name": "CategoryDeactivation"
}
```

### PUT /api/categories/{id}/activate
**Description:** Activate category
**Parameters:** transition_name: "CategoryReactivation"

**Request Example:**
```json
{
  "transition_name": "CategoryReactivation"
}
```

---

## UserRoutes

### GET /api/users
**Description:** Get all users (admin only)
**Parameters:** 
- status (optional): Filter by user state
- user_type (optional): Filter by user type

### GET /api/users/{id}
**Description:** Get user by ID

### POST /api/users/register
**Description:** Register new user
**Parameters:** transition_name: null (automatic transition to Active)

**Request Example:**
```json
{
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "phone": "+1234567890",
  "address": "123 Main St, City, State",
  "user_type": "CUSTOMER"
}
```

**Response Example:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "state": "Active",
  "created_at": "2024-01-01T10:00:00"
}
```

### PUT /api/users/{id}
**Description:** Update user profile
**Parameters:** transition_name: null (no state change)

### PUT /api/users/{id}/suspend
**Description:** Suspend user (admin only)
**Parameters:** transition_name: "UserSuspension"

**Request Example:**
```json
{
  "reason": "Policy violation",
  "admin_id": 1,
  "transition_name": "UserSuspension"
}
```

### PUT /api/users/{id}/activate
**Description:** Activate user (admin only)
**Parameters:** transition_name: "UserReactivation"

**Request Example:**
```json
{
  "admin_id": 1,
  "transition_name": "UserReactivation"
}
```

### PUT /api/users/{id}/deactivate
**Description:** Deactivate user
**Parameters:** transition_name: "UserDeactivation"

**Request Example:**
```json
{
  "transition_name": "UserDeactivation"
}
```
