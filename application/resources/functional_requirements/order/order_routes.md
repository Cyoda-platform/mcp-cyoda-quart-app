# Order Routes

## Description
REST API endpoints for managing orders in the Purrfect Pets store.

## Endpoints

### GET /orders
Get all orders with optional filtering by status.

**Request Example:**
```
GET /orders?status=placed
```

**Response Example:**
```json
[
  {
    "id": "order-123",
    "pet_id": "pet-456",
    "user_id": "user-789",
    "quantity": 1,
    "ship_date": "2024-01-15",
    "total_amount": 299.99,
    "meta": {"state": "placed"}
  }
]
```

### GET /orders/{id}
Get a specific order by ID.

**Request Example:**
```
GET /orders/order-123
```

**Response Example:**
```json
{
  "id": "order-123",
  "pet_id": "pet-456",
  "user_id": "user-789",
  "quantity": 1,
  "ship_date": "2024-01-15",
  "total_amount": 299.99,
  "meta": {"state": "placed"}
}
```

### POST /orders
Create a new order.

**Request Example:**
```json
{
  "pet_id": "pet-456",
  "user_id": "user-789",
  "quantity": 1,
  "ship_date": "2024-01-15",
  "total_amount": 299.99
}
```

**Response Example:**
```json
{
  "id": "order-124"
}
```

### PUT /orders/{id}
Update an order with optional transition.

**Request Example:**
```json
{
  "pet_id": "pet-456",
  "user_id": "user-789",
  "quantity": 1,
  "ship_date": "2024-01-20",
  "total_amount": 299.99,
  "transition": "approve_order"
}
```

**Response Example:**
```json
{
  "success": true
}
```

### DELETE /orders/{id}
Delete an order.

**Request Example:**
```
DELETE /orders/order-123
```

**Response Example:**
```json
{
  "success": true
}
```
