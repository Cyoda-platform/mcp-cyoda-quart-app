# Order API Routes

## Base Route: `/api/orders`

### Endpoints:

**POST /api/orders** - Create new order
- **Request**: `{"petId": 123, "quantity": 1, "shipDate": "2024-01-15T10:00:00Z", "status": "placed", "complete": false}`
- **Response**: `{"id": "456", "petId": 123, "quantity": 1, "shipDate": "2024-01-15T10:00:00Z", "status": "placed", "complete": false}`

**GET /api/orders/{id}** - Get order by ID
- **Response**: `{"id": "456", "petId": 123, "quantity": 1, "shipDate": "2024-01-15T10:00:00Z", "status": "placed", "complete": false}`

**PUT /api/orders/{id}** - Update order with optional transition
- **Request**: `{"status": "approved", "transition": "approve_order"}`
- **Response**: `{"id": "456", "petId": 123, "quantity": 1, "status": "approved", "complete": false}`

**DELETE /api/orders/{id}** - Delete order
- **Response**: `{"message": "Order deleted successfully"}`

**GET /api/orders** - Get all orders
- **Response**: `[{"id": "456", "petId": 123, "quantity": 1, "status": "placed", "complete": false}]`
