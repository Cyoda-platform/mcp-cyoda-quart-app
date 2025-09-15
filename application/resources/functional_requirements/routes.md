# Routes for Purrfect Pets API

## PetRoutes

### GET /pets
**Description:** Get all pets with optional filtering
**Parameters:**
- status: String (optional) - Filter by pet state
- category: Long (optional) - Filter by category ID
- tags: String (optional) - Filter by tags (comma-separated)
- limit: Integer (optional, default: 20)
- offset: Integer (optional, default: 0)

**Request Example:**
```
GET /pets?status=AVAILABLE&category=1&limit=10&offset=0
```

**Response Example:**
```json
{
  "pets": [
    {
      "id": 1,
      "name": "Fluffy",
      "category_id": 1,
      "state": "AVAILABLE",
      "price": 299.99
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

### GET /pets/{id}
**Description:** Get pet by ID
**Parameters:**
- id: Long (path parameter)

**Request Example:**
```
GET /pets/1
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Fluffy",
  "category_id": 1,
  "photo_urls": ["http://example.com/fluffy1.jpg"],
  "tags": ["friendly", "playful"],
  "breed": "Persian",
  "age": 2,
  "weight": 4.5,
  "color": "White",
  "description": "Beautiful white Persian cat",
  "price": 299.99,
  "state": "AVAILABLE",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### POST /pets
**Description:** Create a new pet
**Transition:** null (automatic workflow transition)

**Request Example:**
```json
{
  "name": "Buddy",
  "category_id": 2,
  "photo_urls": ["http://example.com/buddy1.jpg"],
  "tags": ["energetic", "loyal"],
  "breed": "Golden Retriever",
  "age": 1,
  "weight": 25.0,
  "color": "Golden",
  "description": "Friendly golden retriever puppy",
  "price": 599.99
}
```

**Response Example:**
```json
{
  "id": 2,
  "name": "Buddy",
  "state": "DRAFT",
  "message": "Pet created successfully"
}
```

### PUT /pets/{id}
**Description:** Update pet information
**Parameters:**
- id: Long (path parameter)
- transition: String (optional) - Transition name for state change

**Request Example:**
```json
{
  "name": "Buddy Updated",
  "description": "Updated description",
  "price": 649.99,
  "transition": null
}
```

**Response Example:**
```json
{
  "id": 2,
  "name": "Buddy Updated",
  "state": "AVAILABLE",
  "message": "Pet updated successfully"
}
```

### PUT /pets/{id}/transition
**Description:** Transition pet to different state
**Parameters:**
- id: Long (path parameter)
- transition: String (required) - Transition name

**Request Example:**
```json
{
  "transition": "AVAILABLE_TO_UNAVAILABLE"
}
```

**Response Example:**
```json
{
  "id": 2,
  "state": "UNAVAILABLE",
  "message": "Pet transitioned successfully"
}
```

### DELETE /pets/{id}
**Description:** Delete pet (soft delete)
**Parameters:**
- id: Long (path parameter)

## CategoryRoutes

### GET /categories
**Description:** Get all categories

**Request Example:**
```
GET /categories
```

**Response Example:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Cats",
      "description": "Feline companions",
      "state": "ACTIVE"
    }
  ]
}
```

### GET /categories/{id}
**Description:** Get category by ID
**Parameters:**
- id: Long (path parameter)

**Request Example:**
```
GET /categories/1
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Cats",
  "description": "Feline companions",
  "state": "ACTIVE",
  "created_at": "2024-01-01T09:00:00Z",
  "updated_at": "2024-01-01T09:00:00Z"
}
```

### POST /categories
**Description:** Create a new category
**Transition:** null (automatic workflow transition)

**Request Example:**
```json
{
  "name": "Birds",
  "description": "Feathered friends"
}
```

**Response Example:**
```json
{
  "id": 3,
  "name": "Birds",
  "state": "DRAFT",
  "message": "Category created successfully"
}
```

### PUT /categories/{id}
**Description:** Update category
**Parameters:**
- id: Long (path parameter)
- transition: String (optional) - Transition name

**Request Example:**
```json
{
  "name": "Birds Updated",
  "description": "Updated description",
  "transition": null
}
```

### PUT /categories/{id}/transition
**Description:** Transition category state
**Parameters:**
- id: Long (path parameter)
- transition: String (required)

**Request Example:**
```json
{
  "transition": "ACTIVE_TO_INACTIVE"
}
```

## CustomerRoutes

### GET /customers
**Description:** Get all customers (admin only)
**Parameters:**
- status: String (optional) - Filter by customer state
- limit: Integer (optional, default: 20)
- offset: Integer (optional, default: 0)

**Request Example:**
```
GET /customers?status=ACTIVE&limit=10&offset=0
```

**Response Example:**
```json
{
  "customers": [
    {
      "id": 1,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "state": "ACTIVE"
    }
  ]
}
```

### GET /customers/{id}
**Description:** Get customer by ID
**Parameters:**
- id: Long (path parameter)

**Request Example:**
```
GET /customers/1
```

**Response Example:**
```json
{
  "id": 1,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "Anytown",
  "state": "ACTIVE",
  "created_at": "2024-01-01T08:00:00Z"
}
```

### POST /customers
**Description:** Register a new customer
**Transition:** null (automatic workflow transition)

**Request Example:**
```json
{
  "username": "jane_smith",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "+1987654321",
  "address": "456 Oak Ave",
  "city": "Somewhere",
  "state": "CA",
  "zip_code": "12345",
  "country": "USA"
}
```

**Response Example:**
```json
{
  "id": 2,
  "username": "jane_smith",
  "state": "PENDING_VERIFICATION",
  "message": "Customer registered successfully. Please check email for verification."
}
```

### PUT /customers/{id}
**Description:** Update customer information
**Parameters:**
- id: Long (path parameter)
- transition: String (optional)

**Request Example:**
```json
{
  "first_name": "Jane Updated",
  "phone": "+1555666777",
  "transition": null
}
```

### PUT /customers/{id}/transition
**Description:** Transition customer state
**Parameters:**
- id: Long (path parameter)
- transition: String (required)

**Request Example:**
```json
{
  "transition": "ACTIVE_TO_SUSPENDED",
  "reason": "Policy violation"
}
```

## OrderRoutes

### GET /orders
**Description:** Get orders (filtered by customer for regular users)
**Parameters:**
- customer_id: Long (optional, admin only)
- status: String (optional)
- limit: Integer (optional, default: 20)
- offset: Integer (optional, default: 0)

**Request Example:**
```
GET /orders?status=PLACED&limit=10&offset=0
```

**Response Example:**
```json
{
  "orders": [
    {
      "id": 1,
      "customer_id": 1,
      "order_date": "2024-01-01T12:00:00Z",
      "total_amount": 299.99,
      "state": "PLACED"
    }
  ]
}
```

### GET /orders/{id}
**Description:** Get order by ID
**Parameters:**
- id: Long (path parameter)

**Request Example:**
```
GET /orders/1
```

**Response Example:**
```json
{
  "id": 1,
  "customer_id": 1,
  "order_date": "2024-01-01T12:00:00Z",
  "total_amount": 299.99,
  "shipping_address": "123 Main St",
  "state": "PLACED",
  "order_items": [
    {
      "id": 1,
      "pet_id": 1,
      "quantity": 1,
      "unit_price": 299.99,
      "total_price": 299.99
    }
  ]
}
```

### POST /orders
**Description:** Create a new order
**Transition:** null (automatic workflow transition)

**Request Example:**
```json
{
  "customer_id": 1,
  "shipping_address": "123 Main St",
  "shipping_city": "Anytown",
  "shipping_state": "CA",
  "shipping_zip": "12345",
  "shipping_country": "USA",
  "order_items": [
    {
      "pet_id": 1,
      "quantity": 1,
      "unit_price": 299.99
    }
  ]
}
```

**Response Example:**
```json
{
  "id": 1,
  "state": "DRAFT",
  "total_amount": 299.99,
  "message": "Order created successfully"
}
```

### PUT /orders/{id}
**Description:** Update order
**Parameters:**
- id: Long (path parameter)
- transition: String (optional)

**Request Example:**
```json
{
  "shipping_address": "456 Updated St",
  "transition": "DRAFT_TO_PLACED"
}
```

### PUT /orders/{id}/transition
**Description:** Transition order state
**Parameters:**
- id: Long (path parameter)
- transition: String (required)

**Request Example:**
```json
{
  "transition": "APPROVED_TO_SHIPPED",
  "tracking_number": "TRK123456789"
}
```

## OrderItemRoutes

### GET /orders/{orderId}/items
**Description:** Get order items for an order
**Parameters:**
- orderId: Long (path parameter)

**Request Example:**
```
GET /orders/1/items
```

**Response Example:**
```json
{
  "order_items": [
    {
      "id": 1,
      "order_id": 1,
      "pet_id": 1,
      "quantity": 1,
      "unit_price": 299.99,
      "total_price": 299.99,
      "state": "CONFIRMED"
    }
  ]
}
```

### POST /orders/{orderId}/items
**Description:** Add item to order
**Parameters:**
- orderId: Long (path parameter)
**Transition:** null (automatic workflow transition)

**Request Example:**
```json
{
  "pet_id": 2,
  "quantity": 1,
  "unit_price": 599.99
}
```

**Response Example:**
```json
{
  "id": 2,
  "order_id": 1,
  "state": "DRAFT",
  "message": "Order item added successfully"
}
```

### PUT /orders/{orderId}/items/{itemId}
**Description:** Update order item
**Parameters:**
- orderId: Long (path parameter)
- itemId: Long (path parameter)
- transition: String (optional)

**Request Example:**
```json
{
  "quantity": 2,
  "transition": "DRAFT_TO_CONFIRMED"
}
```

### DELETE /orders/{orderId}/items/{itemId}
**Description:** Remove item from order
**Parameters:**
- orderId: Long (path parameter)
- itemId: Long (path parameter)
**Transition:** DRAFT_TO_CANCELLED
