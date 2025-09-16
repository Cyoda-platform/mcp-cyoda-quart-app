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

---

## OrderRoutes

### GET /api/orders
**Description:** Get orders for current user or all orders (admin)
**Parameters:**
- status (optional): Filter by order state
- user_id (optional, admin only): Filter by user
- page (optional): Page number
- size (optional): Page size

**Request Example:**
```
GET /api/orders?status=Placed&page=0&size=10
```

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "user_id": 1,
      "order_date": "2024-01-01T10:00:00",
      "total_amount": 1300.0,
      "state": "Placed"
    }
  ],
  "totalElements": 1
}
```

### GET /api/orders/{id}
**Description:** Get order by ID

**Response Example:**
```json
{
  "id": 1,
  "user_id": 1,
  "order_date": "2024-01-01T10:00:00",
  "ship_date": null,
  "total_amount": 1300.0,
  "shipping_address": "123 Main St, City, State",
  "payment_method": "CREDIT_CARD",
  "notes": "Please handle with care",
  "state": "Placed",
  "items": [
    {
      "id": 1,
      "pet_id": 1,
      "quantity": 1,
      "unit_price": 500.0,
      "total_price": 500.0
    }
  ]
}
```

### POST /api/orders
**Description:** Create new order
**Parameters:** transition_name: null (automatic transition to Placed)

**Request Example:**
```json
{
  "user_id": 1,
  "shipping_address": "123 Main St, City, State",
  "payment_method": "CREDIT_CARD",
  "notes": "Please handle with care",
  "items": [
    {
      "pet_id": 1,
      "quantity": 1,
      "unit_price": 500.0
    },
    {
      "pet_id": 2,
      "quantity": 1,
      "unit_price": 800.0
    }
  ]
}
```

### PUT /api/orders/{id}/approve
**Description:** Approve order
**Parameters:** transition_name: "OrderApproval"

**Request Example:**
```json
{
  "admin_id": 1,
  "transition_name": "OrderApproval"
}
```

### PUT /api/orders/{id}/cancel
**Description:** Cancel order
**Parameters:** transition_name: "OrderCancellation"

**Request Example:**
```json
{
  "reason": "Customer request",
  "admin_approved": false,
  "transition_name": "OrderCancellation"
}
```

### PUT /api/orders/{id}/prepare
**Description:** Start order preparation
**Parameters:** transition_name: "OrderPreparation"

**Request Example:**
```json
{
  "fulfillment_team_id": 1,
  "transition_name": "OrderPreparation"
}
```

### PUT /api/orders/{id}/ship
**Description:** Ship order
**Parameters:** transition_name: "OrderShipping"

**Request Example:**
```json
{
  "tracking_number": "TRK123456789",
  "carrier": "FedEx",
  "estimated_delivery": "2024-01-05",
  "transition_name": "OrderShipping"
}
```

### PUT /api/orders/{id}/deliver
**Description:** Mark order as delivered
**Parameters:** transition_name: "OrderDelivery"

**Request Example:**
```json
{
  "delivery_confirmation": "Delivered to recipient",
  "delivered_by": "John Delivery",
  "transition_name": "OrderDelivery"
}
```

---

## InventoryRoutes

### GET /api/inventory
**Description:** Get all inventory records
**Parameters:**
- status (optional): Filter by inventory state
- low_stock (optional): Show only low stock items

**Request Example:**
```
GET /api/inventory?status=LowStock
```

**Response Example:**
```json
[
  {
    "id": 1,
    "pet_id": 1,
    "quantity": 2,
    "reserved_quantity": 1,
    "reorder_level": 5,
    "state": "LowStock"
  }
]
```

### GET /api/inventory/{id}
**Description:** Get inventory by ID

### GET /api/inventory/pet/{petId}
**Description:** Get inventory for specific pet

### PUT /api/inventory/{id}/restock
**Description:** Restock inventory
**Parameters:** transition_name: null (automatic state evaluation)

**Request Example:**
```json
{
  "quantity": 10,
  "supplier": "Pet Supplier Inc",
  "cost_per_unit": 400.0
}
```

### PUT /api/inventory/{id}/discontinue
**Description:** Discontinue inventory
**Parameters:** transition_name: "InventoryDiscontinuation"

**Request Example:**
```json
{
  "reason": "Product discontinued by supplier",
  "transition_name": "InventoryDiscontinuation"
}
```

---

## ReviewRoutes

### GET /api/reviews
**Description:** Get reviews with filtering
**Parameters:**
- pet_id (optional): Filter by pet
- user_id (optional): Filter by user
- status (optional): Filter by review state
- rating (optional): Filter by rating

**Request Example:**
```
GET /api/reviews?pet_id=1&status=Approved
```

**Response Example:**
```json
[
  {
    "id": 1,
    "pet_id": 1,
    "user_id": 1,
    "rating": 5,
    "comment": "Amazing pet, very friendly!",
    "helpful_count": 3,
    "state": "Approved",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

### GET /api/reviews/{id}
**Description:** Get review by ID

### POST /api/reviews
**Description:** Submit new review
**Parameters:** transition_name: null (automatic transition to Pending)

**Request Example:**
```json
{
  "pet_id": 1,
  "user_id": 1,
  "rating": 5,
  "comment": "Amazing pet, very friendly and well-trained!"
}
```

### PUT /api/reviews/{id}/approve
**Description:** Approve review (moderator only)
**Parameters:** transition_name: "ReviewApproval"

**Request Example:**
```json
{
  "moderator_id": 1,
  "transition_name": "ReviewApproval"
}
```

### PUT /api/reviews/{id}/reject
**Description:** Reject review (moderator only)
**Parameters:** transition_name: "ReviewRejection"

**Request Example:**
```json
{
  "moderator_id": 1,
  "reason": "Inappropriate content",
  "transition_name": "ReviewRejection"
}
```

### PUT /api/reviews/{id}/helpful
**Description:** Mark review as helpful

**Request Example:**
```json
{
  "user_id": 2
}
```

### DELETE /api/reviews/{id}
**Description:** Delete review (author or moderator only)
