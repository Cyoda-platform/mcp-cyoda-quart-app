# Routes for Purrfect Pets API

## PetRoutes

### GET /pets
**Description:** Get all pets with optional filtering
**Parameters:**
- status: String (optional) - Filter by pet status (available, pending, sold)
- category_id: Long (optional) - Filter by category
- tags: String (optional) - Filter by tags (comma-separated)
**Response Example:**
```json
[
  {
    "id": 1,
    "name": "Fluffy",
    "category_id": 1,
    "photo_urls": ["http://example.com/photo1.jpg"],
    "tags": ["friendly", "vaccinated"],
    "breed": "Persian",
    "age": 2,
    "weight": 4.5,
    "color": "white",
    "price": 500.0,
    "status": "available"
  }
]
```

### GET /pets/{petId}
**Description:** Get pet by ID
**Parameters:**
- petId: Long (path parameter)
**Response Example:**
```json
{
  "id": 1,
  "name": "Fluffy",
  "category_id": 1,
  "photo_urls": ["http://example.com/photo1.jpg"],
  "tags": ["friendly", "vaccinated"],
  "breed": "Persian",
  "age": 2,
  "weight": 4.5,
  "color": "white",
  "description": "Beautiful Persian cat",
  "price": 500.0,
  "vaccination_status": true,
  "status": "available"
}
```

### POST /pets
**Description:** Add a new pet
**Transition:** null (automatic initial → available)
**Request Example:**
```json
{
  "name": "Buddy",
  "category_id": 2,
  "photo_urls": ["http://example.com/buddy1.jpg"],
  "tags": ["playful", "trained"],
  "breed": "Golden Retriever",
  "age": 1,
  "weight": 25.0,
  "color": "golden",
  "description": "Friendly and energetic puppy",
  "price": 800.0,
  "vaccination_status": true
}
```
**Response Example:**
```json
{
  "id": 2,
  "name": "Buddy",
  "status": "available",
  "message": "Pet added successfully"
}
```

### PUT /pets/{petId}
**Description:** Update pet information
**Parameters:**
- petId: Long (path parameter)
- transition: String (optional) - Transition name (reserve, release, sell, make_unavailable, make_available, return)
**Request Example:**
```json
{
  "name": "Buddy Updated",
  "description": "Updated description",
  "price": 850.0,
  "transition": "reserve"
}
```
**Response Example:**
```json
{
  "id": 2,
  "name": "Buddy Updated",
  "status": "pending",
  "message": "Pet updated and reserved successfully"
}
```

### DELETE /pets/{petId}
**Description:** Delete pet
**Parameters:**
- petId: Long (path parameter)

## CategoryRoutes

### GET /categories
**Description:** Get all categories
**Response Example:**
```json
[
  {
    "id": 1,
    "name": "Cats",
    "description": "Feline companions",
    "status": "active"
  }
]
```

### GET /categories/{categoryId}
**Description:** Get category by ID
**Parameters:**
- categoryId: Long (path parameter)

### POST /categories
**Description:** Create new category
**Transition:** null (automatic initial → active)
**Request Example:**
```json
{
  "name": "Birds",
  "description": "Feathered friends"
}
```

### PUT /categories/{categoryId}
**Description:** Update category
**Parameters:**
- categoryId: Long (path parameter)
- transition: String (optional) - Transition name (activate, deactivate)
**Request Example:**
```json
{
  "name": "Birds Updated",
  "description": "Updated description",
  "transition": "deactivate"
}
```

### DELETE /categories/{categoryId}
**Description:** Delete category
**Parameters:**
- categoryId: Long (path parameter)

## UserRoutes

### GET /users
**Description:** Get all users (admin only)
**Response Example:**
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "status": "active"
  }
]
```

### GET /users/{userId}
**Description:** Get user by ID
**Parameters:**
- userId: Long (path parameter)

### POST /users
**Description:** Create new user
**Transition:** null (automatic initial → active)
**Request Example:**
```json
{
  "username": "jane_smith",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "password": "securepassword123",
  "phone": "+1234567890",
  "address": "123 Main St, City, State",
  "user_type": "customer"
}
```

### PUT /users/{userId}
**Description:** Update user
**Parameters:**
- userId: Long (path parameter)
- transition: String (optional) - Transition name (activate, deactivate, suspend)
**Request Example:**
```json
{
  "first_name": "Jane Updated",
  "phone": "+1987654321",
  "transition": "suspend"
}
```

### DELETE /users/{userId}
**Description:** Delete user
**Parameters:**
- userId: Long (path parameter)

## OrderRoutes

### GET /orders
**Description:** Get all orders for current user
**Parameters:**
- status: String (optional) - Filter by order status
**Response Example:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "order_date": "2024-01-15T10:30:00Z",
    "total_amount": 1300.0,
    "status": "delivered"
  }
]
```

### GET /orders/{orderId}
**Description:** Get order by ID
**Parameters:**
- orderId: Long (path parameter)

### POST /orders
**Description:** Create new order
**Transition:** null (automatic initial → placed)
**Request Example:**
```json
{
  "user_id": 1,
  "shipping_address": "456 Oak Ave, City, State",
  "payment_method": "credit_card",
  "notes": "Please handle with care",
  "items": [
    {
      "pet_id": 1,
      "quantity": 1
    },
    {
      "pet_id": 2,
      "quantity": 1
    }
  ]
}
```

### PUT /orders/{orderId}
**Description:** Update order
**Parameters:**
- orderId: Long (path parameter)
- transition: String (optional) - Transition name (approve, ship, deliver, cancel)
**Request Example:**
```json
{
  "shipping_address": "Updated address",
  "transition": "ship"
}
```

### DELETE /orders/{orderId}
**Description:** Cancel order
**Parameters:**
- orderId: Long (path parameter)
- transition: String (required) - Must be "cancel"
