# Controllers Specification for Purrfect Pets API

## Overview
This document defines the REST API controllers and routes for the Purrfect Pets API application.

## 1. PetRoutes

### GET /pets
**Description**: Get all pets with optional filtering  
**Parameters**: 
- `status` (query, optional): Filter by pet status (AVAILABLE, PENDING, SOLD, RESERVED, UNAVAILABLE)
- `category` (query, optional): Filter by category ID
- `tags` (query, optional): Filter by tag names (comma-separated)
- `page` (query, optional): Page number (default: 0)
- `size` (query, optional): Page size (default: 20)

**Request Example**:
```
GET /pets?status=AVAILABLE&category=1&tags=friendly,trained&page=0&size=10
```

**Response Example**:
```json
{
  "content": [
    {
      "id": 1,
      "name": "Buddy",
      "category": {"id": 1, "name": "Dogs"},
      "photoUrls": ["https://example.com/buddy1.jpg"],
      "tags": [{"id": 1, "name": "friendly"}],
      "status": "AVAILABLE",
      "price": 500.00
    }
  ],
  "totalElements": 25,
  "totalPages": 3,
  "size": 10,
  "number": 0
}
```

### GET /pets/{petId}
**Description**: Get pet by ID  
**Parameters**: 
- `petId` (path, required): Pet ID

**Request Example**:
```
GET /pets/1
```

**Response Example**:
```json
{
  "id": 1,
  "name": "Buddy",
  "category": {"id": 1, "name": "Dogs"},
  "photoUrls": ["https://example.com/buddy1.jpg"],
  "tags": [{"id": 1, "name": "friendly"}],
  "status": "AVAILABLE",
  "price": 500.00,
  "description": "Friendly golden retriever",
  "breed": "Golden Retriever",
  "birthDate": "2022-01-15",
  "weight": 25.5,
  "vaccinated": true,
  "neutered": false
}
```

### POST /pets
**Description**: Add a new pet  
**Parameters**: 
- `transitionName` (query, optional): Transition name (null for initial creation)

**Request Example**:
```json
{
  "name": "Max",
  "category": {"id": 1},
  "photoUrls": ["https://example.com/max1.jpg"],
  "tags": [{"id": 1}, {"id": 2}],
  "price": 600.00,
  "description": "Playful labrador",
  "breed": "Labrador",
  "birthDate": "2023-03-10",
  "weight": 20.0,
  "vaccinated": true,
  "neutered": true
}
```

**Response Example**:
```json
{
  "id": 2,
  "name": "Max",
  "status": "AVAILABLE",
  "message": "Pet created successfully"
}
```

### PUT /pets/{petId}
**Description**: Update an existing pet  
**Parameters**: 
- `petId` (path, required): Pet ID
- `transitionName` (query, optional): Transition name for state change

**Request Example**:
```
PUT /pets/1?transitionName=reserve
```
```json
{
  "name": "Buddy Updated",
  "price": 550.00,
  "description": "Very friendly golden retriever"
}
```

**Response Example**:
```json
{
  "id": 1,
  "name": "Buddy Updated",
  "status": "RESERVED",
  "message": "Pet updated successfully"
}
```

### DELETE /pets/{petId}
**Description**: Delete a pet (mark as unavailable)  
**Parameters**: 
- `petId` (path, required): Pet ID
- `transitionName` (query, required): "markUnavailable"

**Request Example**:
```
DELETE /pets/1?transitionName=markUnavailable
```

**Response Example**:
```json
{
  "message": "Pet marked as unavailable successfully"
}
```

## 2. CategoryRoutes

### GET /categories
**Description**: Get all categories

**Request Example**:
```
GET /categories
```

**Response Example**:
```json
[
  {
    "id": 1,
    "name": "Dogs",
    "description": "All dog breeds",
    "status": "ACTIVE"
  },
  {
    "id": 2,
    "name": "Cats",
    "description": "All cat breeds",
    "status": "ACTIVE"
  }
]
```

### GET /categories/{categoryId}
**Description**: Get category by ID  
**Parameters**: 
- `categoryId` (path, required): Category ID

**Request Example**:
```
GET /categories/1
```

**Response Example**:
```json
{
  "id": 1,
  "name": "Dogs",
  "description": "All dog breeds",
  "status": "ACTIVE"
}
```

### POST /categories
**Description**: Create a new category  
**Parameters**: 
- `transitionName` (query, optional): null for initial creation

**Request Example**:
```json
{
  "name": "Birds",
  "description": "All bird species"
}
```

**Response Example**:
```json
{
  "id": 3,
  "name": "Birds",
  "status": "ACTIVE",
  "message": "Category created successfully"
}
```

### PUT /categories/{categoryId}
**Description**: Update a category  
**Parameters**: 
- `categoryId` (path, required): Category ID
- `transitionName` (query, optional): "activate" or "deactivate"

**Request Example**:
```
PUT /categories/1?transitionName=deactivate
```
```json
{
  "name": "Dogs Updated",
  "description": "Updated description"
}
```

**Response Example**:
```json
{
  "id": 1,
  "name": "Dogs Updated",
  "status": "INACTIVE",
  "message": "Category updated successfully"
}
```

## 3. TagRoutes

### GET /tags
**Description**: Get all tags

**Request Example**:
```
GET /tags
```

**Response Example**:
```json
[
  {
    "id": 1,
    "name": "friendly",
    "color": "#green",
    "status": "ACTIVE"
  },
  {
    "id": 2,
    "name": "trained",
    "color": "#blue",
    "status": "ACTIVE"
  }
]
```

### POST /tags
**Description**: Create a new tag  
**Parameters**: 
- `transitionName` (query, optional): null for initial creation

**Request Example**:
```json
{
  "name": "hypoallergenic",
  "color": "#purple"
}
```

**Response Example**:
```json
{
  "id": 3,
  "name": "hypoallergenic",
  "status": "ACTIVE",
  "message": "Tag created successfully"
}
```

## 4. UserRoutes

### POST /users
**Description**: Register a new user  
**Parameters**: 
- `transitionName` (query, optional): null for initial registration

**Request Example**:
```json
{
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "password": "securePassword123",
  "phone": "+1234567890",
  "role": "CUSTOMER",
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zipCode": "12345",
    "country": "USA"
  }
}
```

**Response Example**:
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john.doe@example.com",
  "status": "PENDING_VERIFICATION",
  "message": "User registered successfully. Please check your email for verification."
}
```

### POST /users/verify
**Description**: Verify user email  
**Parameters**: 
- `transitionName` (query, required): "verify"

**Request Example**:
```json
{
  "email": "john.doe@example.com",
  "verificationToken": "abc123xyz789"
}
```

**Response Example**:
```json
{
  "message": "Email verified successfully. Account is now active."
}
```

### GET /users/{userId}
**Description**: Get user by ID  
**Parameters**: 
- `userId` (path, required): User ID

**Request Example**:
```
GET /users/1
```

**Response Example**:
```json
{
  "id": 1,
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "status": "ACTIVE",
  "role": "CUSTOMER",
  "registrationDate": "2024-01-15T10:30:00"
}
```

### PUT /users/{userId}
**Description**: Update user information  
**Parameters**: 
- `userId` (path, required): User ID
- `transitionName` (query, optional): "suspend", "activate", or null

**Request Example**:
```
PUT /users/1?transitionName=suspend
```
```json
{
  "firstName": "John Updated",
  "phone": "+1987654321",
  "suspensionReason": "Policy violation"
}
```

**Response Example**:
```json
{
  "id": 1,
  "status": "SUSPENDED",
  "message": "User updated and suspended successfully"
}
```

## 5. OrderRoutes

### POST /orders
**Description**: Create a new order  
**Parameters**: 
- `transitionName` (query, optional): null for initial creation

**Request Example**:
```json
{
  "userId": 1,
  "items": [
    {
      "petId": 1,
      "quantity": 1
    },
    {
      "petId": 2,
      "quantity": 1
    }
  ],
  "shippingAddress": {
    "street": "456 Oak Ave",
    "city": "Somewhere",
    "state": "NY",
    "zipCode": "67890",
    "country": "USA"
  },
  "paymentMethod": "CREDIT_CARD",
  "notes": "Please handle with care"
}
```

**Response Example**:
```json
{
  "id": 1,
  "userId": 1,
  "status": "PLACED",
  "totalAmount": 1100.00,
  "orderDate": "2024-01-15T14:30:00",
  "message": "Order created successfully"
}
```

### GET /orders/{orderId}
**Description**: Get order by ID  
**Parameters**: 
- `orderId` (path, required): Order ID

**Request Example**:
```
GET /orders/1
```

**Response Example**:
```json
{
  "id": 1,
  "userId": 1,
  "status": "PLACED",
  "orderDate": "2024-01-15T14:30:00",
  "totalAmount": 1100.00,
  "items": [
    {
      "id": 1,
      "petId": 1,
      "petName": "Buddy",
      "quantity": 1,
      "unitPrice": 500.00,
      "totalPrice": 500.00,
      "status": "PENDING"
    }
  ],
  "shippingAddress": {
    "street": "456 Oak Ave",
    "city": "Somewhere",
    "state": "NY",
    "zipCode": "67890",
    "country": "USA"
  }
}
```

### PUT /orders/{orderId}
**Description**: Update order status  
**Parameters**: 
- `orderId` (path, required): Order ID
- `transitionName` (query, required): "approve", "deliver", or "cancel"

**Request Example**:
```
PUT /orders/1?transitionName=approve
```
```json
{
  "notes": "Order approved for processing"
}
```

**Response Example**:
```json
{
  "id": 1,
  "status": "APPROVED",
  "message": "Order approved successfully"
}
```

### GET /users/{userId}/orders
**Description**: Get orders for a specific user  
**Parameters**: 
- `userId` (path, required): User ID
- `status` (query, optional): Filter by order status

**Request Example**:
```
GET /users/1/orders?status=PLACED
```

**Response Example**:
```json
[
  {
    "id": 1,
    "status": "PLACED",
    "orderDate": "2024-01-15T14:30:00",
    "totalAmount": 1100.00
  }
]
```

## 6. AddressRoutes

### POST /addresses
**Description**: Create a new address  
**Parameters**: 
- `transitionName` (query, optional): null for initial creation

**Request Example**:
```json
{
  "street": "789 Pine St",
  "city": "Newtown",
  "state": "TX",
  "zipCode": "54321",
  "country": "USA"
}
```

**Response Example**:
```json
{
  "id": 1,
  "status": "ACTIVE",
  "message": "Address created successfully"
}
```

### PUT /addresses/{addressId}
**Description**: Update address  
**Parameters**: 
- `addressId` (path, required): Address ID
- `transitionName` (query, optional): "activate" or "deactivate"

**Request Example**:
```
PUT /addresses/1?transitionName=deactivate
```
```json
{
  "street": "789 Pine St Updated",
  "city": "Newtown Updated"
}
```

**Response Example**:
```json
{
  "id": 1,
  "status": "INACTIVE",
  "message": "Address updated successfully"
}
```

## API Response Standards

### Success Response Format
```json
{
  "data": { /* entity data */ },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": ["Name is required", "Price must be positive"]
  },
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 500: Internal Server Error

## Authentication & Authorization
- All endpoints require authentication except user registration and email verification
- Use JWT tokens for authentication
- Role-based access control (CUSTOMER, STAFF, ADMIN)
- Users can only access their own data unless they have STAFF or ADMIN role
