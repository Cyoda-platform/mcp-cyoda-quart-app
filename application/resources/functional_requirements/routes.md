# Routes for Purrfect Pets API

## PetRoutes

### GET /api/v1/pets
**Description:** Get all pets with optional filtering
**Parameters:**
- `status` (query, optional): Filter by pet status (available, pending, sold)
- `category` (query, optional): Filter by category name
- `tags` (query, optional): Filter by tags (comma-separated)
- `page` (query, optional): Page number (default: 0)
- `size` (query, optional): Page size (default: 20)

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "name": "Buddy",
      "category": {"id": 1, "name": "Dogs"},
      "status": "available",
      "price": 500.00
    }
  ],
  "totalElements": 50,
  "totalPages": 3
}
```

### GET /api/v1/pets/{petId}
**Description:** Get pet by ID
**Parameters:**
- `petId` (path): Pet ID

**Response Example:**
```json
{
  "id": 1,
  "name": "Buddy",
  "category": {"id": 1, "name": "Dogs"},
  "photoUrls": ["https://example.com/buddy1.jpg"],
  "tags": [{"id": 1, "name": "friendly"}],
  "status": "available",
  "price": 500.00,
  "breed": "Golden Retriever",
  "color": "Golden",
  "weight": 25.5,
  "vaccinated": true
}
```

### POST /api/v1/pets
**Description:** Create a new pet
**Request Body:**
```json
{
  "name": "Buddy",
  "category": {"id": 1},
  "photoUrls": ["https://example.com/buddy1.jpg"],
  "tags": [{"id": 1}],
  "description": "Friendly golden retriever",
  "price": 500.00,
  "breed": "Golden Retriever",
  "color": "Golden",
  "weight": 25.5,
  "vaccinated": true,
  "neutered": false
}
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Buddy",
  "status": "available"
}
```

### PUT /api/v1/pets/{petId}
**Description:** Update pet information
**Parameters:**
- `petId` (path): Pet ID
- `transitionName` (query, optional): Transition name for state change

**Request Body:**
```json
{
  "name": "Buddy Updated",
  "description": "Updated description",
  "price": 550.00,
  "transitionName": "reserve"
}
```

### PUT /api/v1/pets/{petId}/reserve
**Description:** Reserve a pet (available → pending)
**Parameters:**
- `petId` (path): Pet ID
- `transitionName` (query): "reserve"

**Request Body:**
```json
{
  "customerName": "John Doe",
  "customerEmail": "john@example.com",
  "customerPhone": "+1234567890",
  "transitionName": "reserve"
}
```

### PUT /api/v1/pets/{petId}/cancel-reservation
**Description:** Cancel pet reservation (pending → available)
**Parameters:**
- `petId` (path): Pet ID
- `transitionName` (query): "cancel_reservation"

**Request Body:**
```json
{
  "transitionName": "cancel_reservation"
}
```

### PUT /api/v1/pets/{petId}/sell
**Description:** Sell a pet (pending/available → sold)
**Parameters:**
- `petId` (path): Pet ID
- `transitionName` (query): "sell" or "direct_sell"

**Request Body:**
```json
{
  "customerName": "John Doe",
  "customerEmail": "john@example.com",
  "customerPhone": "+1234567890",
  "customerAddress": "123 Main St, City, State",
  "paymentMethod": "credit_card",
  "transitionName": "sell"
}
```

### DELETE /api/v1/pets/{petId}
**Description:** Delete a pet
**Parameters:**
- `petId` (path): Pet ID

## OrderRoutes

### GET /api/v1/orders
**Description:** Get all orders with optional filtering
**Parameters:**
- `status` (query, optional): Filter by order status
- `customerId` (query, optional): Filter by customer ID
- `page` (query, optional): Page number
- `size` (query, optional): Page size

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "petId": 1,
      "customerName": "John Doe",
      "status": "placed",
      "totalAmount": 500.00
    }
  ]
}
```

### GET /api/v1/orders/{orderId}
**Description:** Get order by ID
**Parameters:**
- `orderId` (path): Order ID

**Response Example:**
```json
{
  "id": 1,
  "petId": 1,
  "quantity": 1,
  "customerName": "John Doe",
  "customerEmail": "john@example.com",
  "status": "placed",
  "totalAmount": 500.00,
  "orderDate": "2024-01-15T10:30:00Z"
}
```

### POST /api/v1/orders
**Description:** Create a new order
**Request Body:**
```json
{
  "petId": 1,
  "quantity": 1,
  "customerName": "John Doe",
  "customerEmail": "john@example.com",
  "customerPhone": "+1234567890",
  "customerAddress": "123 Main St, City, State",
  "paymentMethod": "credit_card",
  "notes": "Please call before delivery"
}
```

### PUT /api/v1/orders/{orderId}
**Description:** Update order
**Parameters:**
- `orderId` (path): Order ID
- `transitionName` (query, optional): Transition name

**Request Body:**
```json
{
  "customerAddress": "456 New St, City, State",
  "notes": "Updated delivery address",
  "transitionName": "update"
}
```

### PUT /api/v1/orders/{orderId}/approve
**Description:** Approve order (placed → approved)
**Parameters:**
- `orderId` (path): Order ID
- `transitionName` (query): "approve"

**Request Body:**
```json
{
  "approvedBy": "admin@purrfectpets.com",
  "transitionName": "approve"
}
```

### PUT /api/v1/orders/{orderId}/deliver
**Description:** Mark order as delivered (approved → delivered)
**Parameters:**
- `orderId` (path): Order ID
- `transitionName` (query): "deliver"

**Request Body:**
```json
{
  "deliveredBy": "staff@purrfectpets.com",
  "deliverySignature": "John Doe",
  "deliveryNotes": "Delivered successfully",
  "transitionName": "deliver"
}
```

### DELETE /api/v1/orders/{orderId}
**Description:** Delete an order
**Parameters:**
- `orderId` (path): Order ID

## UserRoutes

### GET /api/v1/users
**Description:** Get all users (admin only)
**Parameters:**
- `status` (query, optional): Filter by user status
- `role` (query, optional): Filter by user role
- `page` (query, optional): Page number
- `size` (query, optional): Page size

### GET /api/v1/users/{userId}
**Description:** Get user by ID
**Parameters:**
- `userId` (path): User ID

### POST /api/v1/users
**Description:** Create a new user (register)
**Request Body:**
```json
{
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "phone": "+1234567890"
}
```

### PUT /api/v1/users/{userId}
**Description:** Update user information
**Parameters:**
- `userId` (path): User ID
- `transitionName` (query, optional): Transition name

**Request Body:**
```json
{
  "firstName": "John Updated",
  "lastName": "Doe Updated",
  "phone": "+1234567891",
  "transitionName": null
}
```

### PUT /api/v1/users/{userId}/deactivate
**Description:** Deactivate user (active → inactive)
**Parameters:**
- `userId` (path): User ID
- `transitionName` (query): "deactivate"

**Request Body:**
```json
{
  "reason": "User requested deactivation",
  "transitionName": "deactivate"
}
```

### PUT /api/v1/users/{userId}/reactivate
**Description:** Reactivate user (inactive → active)
**Parameters:**
- `userId` (path): User ID
- `transitionName` (query): "reactivate"

**Request Body:**
```json
{
  "transitionName": "reactivate"
}
```

### PUT /api/v1/users/{userId}/suspend
**Description:** Suspend user (active → suspended)
**Parameters:**
- `userId` (path): User ID
- `transitionName` (query): "suspend"

**Request Body:**
```json
{
  "reason": "Policy violation",
  "suspensionDuration": 30,
  "transitionName": "suspend"
}
```

### PUT /api/v1/users/{userId}/unsuspend
**Description:** Unsuspend user (suspended → active)
**Parameters:**
- `userId` (path): User ID
- `transitionName` (query): "unsuspend"

**Request Body:**
```json
{
  "transitionName": "unsuspend"
}
```

### DELETE /api/v1/users/{userId}
**Description:** Delete a user
**Parameters:**
- `userId` (path): User ID
