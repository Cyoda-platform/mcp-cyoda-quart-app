# Routes for Purrfect Pets API

## PetRoutes

### GET /api/pets
**Description:** Get all pets with optional filtering
**Parameters:** 
- category (optional): Filter by category
- status (optional): Filter by availability status
- minPrice (optional): Minimum price filter
- maxPrice (optional): Maximum price filter
- page (optional): Page number for pagination
- size (optional): Page size for pagination

**Request Example:**
```
GET /api/pets?category=Dog&status=AVAILABLE&minPrice=100&maxPrice=500&page=0&size=10
```

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "name": "Buddy",
      "category": "Dog",
      "breed": "Golden Retriever",
      "age": 2,
      "color": "Golden",
      "weight": 25.5,
      "price": 350.0,
      "state": "AVAILABLE"
    }
  ],
  "totalElements": 1,
  "totalPages": 1
}
```

### GET /api/pets/{id}
**Description:** Get pet by ID
**Parameters:** 
- id: Pet ID

**Request Example:**
```
GET /api/pets/1
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Buddy",
  "category": "Dog",
  "breed": "Golden Retriever",
  "age": 2,
  "color": "Golden",
  "weight": 25.5,
  "description": "Friendly and energetic dog",
  "price": 350.0,
  "imageUrl": "https://example.com/buddy.jpg",
  "ownerId": null,
  "state": "AVAILABLE",
  "createdAt": "2024-01-15T10:30:00",
  "updatedAt": "2024-01-15T10:30:00"
}
```

### POST /api/pets
**Description:** Create new pet
**Parameters:** Pet data in request body

**Request Example:**
```json
{
  "name": "Max",
  "category": "Dog",
  "breed": "Labrador",
  "age": 1,
  "color": "Black",
  "weight": 20.0,
  "description": "Playful puppy",
  "price": 400.0,
  "imageUrl": "https://example.com/max.jpg"
}
```

**Response Example:**
```json
{
  "id": 2,
  "name": "Max",
  "state": "AVAILABLE",
  "createdAt": "2024-01-15T11:00:00"
}
```

### PUT /api/pets/{id}
**Description:** Update pet
**Parameters:** 
- id: Pet ID
- transitionName (optional): Workflow transition name
- Pet data in request body

**Request Example:**
```json
{
  "transitionName": "AVAILABLE_TO_PENDING",
  "ownerId": 1,
  "name": "Buddy Updated",
  "description": "Updated description"
}
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Buddy Updated",
  "state": "PENDING",
  "updatedAt": "2024-01-15T12:00:00"
}
```

### DELETE /api/pets/{id}
**Description:** Delete pet (soft delete)
**Parameters:** 
- id: Pet ID

**Request Example:**
```
DELETE /api/pets/1
```

**Response Example:**
```json
{
  "message": "Pet deleted successfully"
}
```

## OwnerRoutes

### GET /api/owners
**Description:** Get all owners with pagination
**Parameters:** 
- page (optional): Page number
- size (optional): Page size
- status (optional): Filter by owner status

**Request Example:**
```
GET /api/owners?status=ACTIVE&page=0&size=10
```

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com",
      "state": "ACTIVE"
    }
  ],
  "totalElements": 1
}
```

### GET /api/owners/{id}
**Description:** Get owner by ID
**Parameters:** 
- id: Owner ID

**Request Example:**
```
GET /api/owners/1
```

**Response Example:**
```json
{
  "id": 1,
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "New York",
  "zipCode": "10001",
  "country": "USA",
  "state": "ACTIVE",
  "createdAt": "2024-01-10T09:00:00"
}
```

### POST /api/owners
**Description:** Create new owner
**Parameters:** Owner data in request body

**Request Example:**
```json
{
  "firstName": "Jane",
  "lastName": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1987654321",
  "address": "456 Oak Ave",
  "city": "Los Angeles",
  "zipCode": "90210",
  "country": "USA",
  "dateOfBirth": "1990-05-15"
}
```

**Response Example:**
```json
{
  "id": 2,
  "firstName": "Jane",
  "lastName": "Smith",
  "state": "PENDING_VERIFICATION",
  "createdAt": "2024-01-15T13:00:00"
}
```

### PUT /api/owners/{id}
**Description:** Update owner
**Parameters:**
- id: Owner ID
- transitionName (optional): Workflow transition name
- Owner data in request body

**Request Example:**
```json
{
  "transitionName": "PENDING_VERIFICATION_TO_ACTIVE",
  "verificationToken": "abc123xyz",
  "phone": "+1234567891"
}
```

**Response Example:**
```json
{
  "id": 1,
  "state": "ACTIVE",
  "updatedAt": "2024-01-15T14:00:00"
}
```

## OrderRoutes

### GET /api/orders
**Description:** Get all orders with optional filtering
**Parameters:**
- ownerId (optional): Filter by owner ID
- status (optional): Filter by order status
- fromDate (optional): Filter orders from date
- toDate (optional): Filter orders to date
- page (optional): Page number
- size (optional): Page size

**Request Example:**
```
GET /api/orders?ownerId=1&status=CONFIRMED&page=0&size=10
```

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "ownerId": 1,
      "petId": 1,
      "totalAmount": 350.0,
      "state": "CONFIRMED",
      "orderDate": "2024-01-15T15:00:00"
    }
  ],
  "totalElements": 1
}
```

### GET /api/orders/{id}
**Description:** Get order by ID
**Parameters:**
- id: Order ID

**Request Example:**
```
GET /api/orders/1
```

**Response Example:**
```json
{
  "id": 1,
  "ownerId": 1,
  "petId": 1,
  "quantity": 1,
  "totalAmount": 350.0,
  "orderDate": "2024-01-15T15:00:00",
  "deliveryDate": "2024-01-20",
  "deliveryAddress": "123 Main St, New York, NY 10001",
  "notes": "Please call before delivery",
  "state": "CONFIRMED",
  "createdAt": "2024-01-15T15:00:00",
  "updatedAt": "2024-01-15T15:30:00"
}
```

### POST /api/orders
**Description:** Create new order
**Parameters:** Order data in request body

**Request Example:**
```json
{
  "ownerId": 1,
  "petId": 1,
  "quantity": 1,
  "deliveryAddress": "123 Main St, New York, NY 10001",
  "deliveryDate": "2024-01-20",
  "notes": "Please call before delivery"
}
```

**Response Example:**
```json
{
  "id": 1,
  "ownerId": 1,
  "petId": 1,
  "totalAmount": 350.0,
  "state": "PLACED",
  "createdAt": "2024-01-15T15:00:00"
}
```

### PUT /api/orders/{id}
**Description:** Update order
**Parameters:**
- id: Order ID
- transitionName (optional): Workflow transition name
- Order data in request body

**Request Example:**
```json
{
  "transitionName": "PLACED_TO_CONFIRMED",
  "notes": "Updated delivery instructions",
  "deliveryDate": "2024-01-22"
}
```

**Response Example:**
```json
{
  "id": 1,
  "state": "CONFIRMED",
  "updatedAt": "2024-01-15T16:00:00"
}
```

### DELETE /api/orders/{id}
**Description:** Cancel order
**Parameters:**
- id: Order ID
- transitionName: Should be "PLACED_TO_CANCELLED" or "CONFIRMED_TO_CANCELLED"

**Request Example:**
```json
{
  "transitionName": "PLACED_TO_CANCELLED",
  "cancellationReason": "Customer request"
}
```

**Response Example:**
```json
{
  "id": 1,
  "state": "CANCELLED",
  "updatedAt": "2024-01-15T16:30:00"
}
```

## CategoryRoutes

### GET /api/categories
**Description:** Get all categories
**Parameters:**
- status (optional): Filter by category status
- page (optional): Page number
- size (optional): Page size

**Request Example:**
```
GET /api/categories?status=ACTIVE&page=0&size=10
```

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "name": "Dogs",
      "description": "All dog breeds",
      "isActive": true,
      "state": "ACTIVE"
    }
  ],
  "totalElements": 1
}
```

### GET /api/categories/{id}
**Description:** Get category by ID
**Parameters:**
- id: Category ID

**Request Example:**
```
GET /api/categories/1
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Dogs",
  "description": "All dog breeds and puppies",
  "imageUrl": "https://example.com/dogs.jpg",
  "isActive": true,
  "state": "ACTIVE",
  "createdAt": "2024-01-01T00:00:00",
  "updatedAt": "2024-01-01T00:00:00"
}
```

### POST /api/categories
**Description:** Create new category
**Parameters:** Category data in request body

**Request Example:**
```json
{
  "name": "Cats",
  "description": "All cat breeds and kittens",
  "imageUrl": "https://example.com/cats.jpg"
}
```

**Response Example:**
```json
{
  "id": 2,
  "name": "Cats",
  "state": "ACTIVE",
  "createdAt": "2024-01-15T17:00:00"
}
```

### PUT /api/categories/{id}
**Description:** Update category
**Parameters:**
- id: Category ID
- transitionName (optional): Workflow transition name
- Category data in request body

**Request Example:**
```json
{
  "transitionName": "ACTIVE_TO_INACTIVE",
  "description": "Updated description for cats"
}
```

**Response Example:**
```json
{
  "id": 2,
  "state": "INACTIVE",
  "updatedAt": "2024-01-15T17:30:00"
}
```

### DELETE /api/categories/{id}
**Description:** Archive category
**Parameters:**
- id: Category ID
- transitionName: Should be "INACTIVE_TO_ARCHIVED"

**Request Example:**
```json
{
  "transitionName": "INACTIVE_TO_ARCHIVED"
}
```

**Response Example:**
```json
{
  "id": 2,
  "state": "ARCHIVED",
  "updatedAt": "2024-01-15T18:00:00"
}
```
