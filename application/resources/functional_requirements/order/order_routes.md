# Order API Routes

## Base Path: `/api/orders`

### 1. Create Order
- **Method**: POST
- **Path**: `/api/orders`
- **Request Body**:
```json
{
  "petId": "pet-123",
  "userId": "user-456",
  "quantity": 1,
  "shippingAddress": {
    "street": "123 Main St",
    "city": "Anytown",
    "zipCode": "12345"
  }
}
```
- **Response**:
```json
{
  "id": "order-789",
  "status": "success",
  "message": "Order created successfully"
}
```

### 2. Get Order by ID
- **Method**: GET
- **Path**: `/api/orders/{orderId}`
- **Response**:
```json
{
  "id": "order-789",
  "petId": "pet-123",
  "userId": "user-456",
  "quantity": 1,
  "totalAmount": 500.00,
  "shipDate": "2024-01-15T10:00:00Z",
  "complete": false,
  "state": "placed",
  "shippingAddress": {
    "street": "123 Main St",
    "city": "Anytown",
    "zipCode": "12345"
  }
}
```

### 3. Update Order
- **Method**: PUT
- **Path**: `/api/orders/{orderId}`
- **Query Parameters**: `transition` (optional) - transition name for state change
- **Request Body**:
```json
{
  "shipDate": "2024-01-20T10:00:00Z",
  "transition": "approve_order"
}
```
- **Response**:
```json
{
  "id": "order-789",
  "status": "success",
  "message": "Order updated and transitioned to approved"
}
```

### 4. Delete Order
- **Method**: DELETE
- **Path**: `/api/orders/{orderId}`
- **Response**:
```json
{
  "status": "success",
  "message": "Order deleted successfully"
}
```

### 5. List Orders
- **Method**: GET
- **Path**: `/api/orders`
- **Query Parameters**: `userId`, `status`, `limit`, `offset`
- **Response**:
```json
{
  "orders": [...],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```
