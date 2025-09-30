# Order API Routes

## Base Path: `/api/orders`

### GET /api/orders
Get all orders
**Response**: Array of order objects

### GET /api/orders/{id}
Get order by ID
**Response**: Order object

### POST /api/orders
Create new order
**Request**:
```json
{
  "userId": "user-123",
  "petId": "pet-456",
  "orderDate": "2024-01-15",
  "totalAmount": 500,
  "paymentMethod": "credit_card",
  "deliveryAddress": "123 Main St, Anytown 12345",
  "specialInstructions": "Please call before delivery",
  "estimatedDeliveryDate": "2024-01-20"
}
```
**Response**: Order ID

### PUT /api/orders/{id}
Update order with optional transition
**Request**:
```json
{
  "totalAmount": 450,
  "transition": "process_payment"
}
```
**Response**: Updated order object

### DELETE /api/orders/{id}
Delete order
**Response**: Success confirmation
