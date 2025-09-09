# Purrfect Pets API - Controller Requirements

## Overview
This document defines the detailed requirements for all API controllers in the Purrfect Pets API system. Each entity has its own routes class with full CRUD operations and workflow transitions.

## 1. PetRoutes

**Class Name**: PetRoutes  
**Base Path**: `/api/v1/pets`  
**Description**: Manages all pet-related API endpoints

### Endpoints

#### GET /api/v1/pets
**Description**: Get all pets with optional filtering  
**Query Parameters**:
- `status` (optional): Filter by pet status (available, pending, sold)
- `category` (optional): Filter by category ID
- `tags` (optional): Filter by tag names (comma-separated)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Request Example**:
```
GET /api/v1/pets?status=available&category=1&limit=10&offset=0
```

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Fluffy",
      "category": {"id": 1, "name": "Cats"},
      "photoUrls": ["https://example.com/fluffy1.jpg"],
      "tags": [{"id": 1, "name": "friendly"}],
      "price": 299.99,
      "status": "available"
    }
  ],
  "pagination": {
    "total": 25,
    "limit": 10,
    "offset": 0
  }
}
```

#### GET /api/v1/pets/{petId}
**Description**: Get a specific pet by ID

**Request Example**:
```
GET /api/v1/pets/1
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Fluffy",
    "category": {"id": 1, "name": "Cats"},
    "photoUrls": ["https://example.com/fluffy1.jpg"],
    "tags": [{"id": 1, "name": "friendly"}],
    "description": "A beautiful Persian cat",
    "price": 299.99,
    "breed": "Persian",
    "age": 12,
    "weight": 4.5,
    "color": "white",
    "gender": "female",
    "vaccinated": true,
    "neutered": true,
    "status": "available",
    "createdAt": "2024-01-15T10:30:00Z"
  }
}
```

#### POST /api/v1/pets
**Description**: Create a new pet  
**Transition**: Triggers `initialize_pet` transition (none → available)

**Request Example**:
```json
{
  "name": "Buddy",
  "category": {"id": 2, "name": "Dogs"},
  "photoUrls": ["https://example.com/buddy1.jpg", "https://example.com/buddy2.jpg"],
  "tags": [{"id": 2, "name": "trained"}, {"id": 3, "name": "vaccinated"}],
  "description": "A friendly Golden Retriever",
  "price": 599.99,
  "breed": "Golden Retriever",
  "age": 24,
  "weight": 25.0,
  "color": "golden",
  "gender": "male",
  "vaccinated": true,
  "neutered": false
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "status": "available"
  }
}
```

#### PUT /api/v1/pets/{petId}
**Description**: Update a pet with optional state transition  
**Query Parameters**:
- `transition` (optional): Transition name (reserve_pet, complete_sale, cancel_reservation)

**Request Example** (Reserve pet):
```
PUT /api/v1/pets/1?transition=reserve_pet

{
  "orderId": 123,
  "userId": 456
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "pending",
    "reservedBy": 456,
    "reservedForOrder": 123
  }
}
```

#### DELETE /api/v1/pets/{petId}
**Description**: Delete a pet (soft delete)

**Response Example**:
```json
{
  "success": true,
  "message": "Pet deleted successfully"
}
```

## 2. OrderRoutes

**Class Name**: OrderRoutes  
**Base Path**: `/api/v1/orders`  
**Description**: Manages all order-related API endpoints

### Endpoints

#### GET /api/v1/orders
**Description**: Get all orders with optional filtering  
**Query Parameters**:
- `userId` (optional): Filter by user ID
- `status` (optional): Filter by order status
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

#### GET /api/v1/orders/{orderId}
**Description**: Get a specific order by ID

#### POST /api/v1/orders
**Description**: Create a new order  
**Transition**: Triggers `place_order` transition (none → placed)

**Request Example**:
```json
{
  "petId": 1,
  "userId": 456,
  "quantity": 1,
  "shippingAddress": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zipCode": "12345",
    "country": "USA"
  },
  "paymentMethod": "credit_card",
  "notes": "Please handle with care"
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "status": "placed",
    "totalAmount": 299.99,
    "shipDate": "2024-01-22T10:30:00Z"
  }
}
```

#### PUT /api/v1/orders/{orderId}
**Description**: Update an order with optional state transition  
**Query Parameters**:
- `transition` (optional): Transition name (approve_order, deliver_order, cancel_order, cancel_approved_order)

**Request Example** (Approve order):
```
PUT /api/v1/orders/123?transition=approve_order

{
  "paymentConfirmation": "PAY_123456789"
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "status": "approved",
    "paymentStatus": "paid"
  }
}
```

#### DELETE /api/v1/orders/{orderId}
**Description**: Cancel an order  
**Transition**: Triggers `cancel_order` transition

## 3. UserRoutes

**Class Name**: UserRoutes  
**Base Path**: `/api/v1/users`  
**Description**: Manages all user-related API endpoints

### Endpoints

#### GET /api/v1/users/{userId}
**Description**: Get a specific user by ID

#### POST /api/v1/users
**Description**: Register a new user  
**Transition**: Triggers `register_user` transition (none → pending_verification)

**Request Example**:
```json
{
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "phone": "+1-555-123-4567",
  "address": {
    "street": "456 Oak Ave",
    "city": "Springfield",
    "state": "IL",
    "zipCode": "62701",
    "country": "USA"
  },
  "dateOfBirth": "1990-05-15",
  "preferences": {
    "newsletter": true,
    "notifications": true,
    "preferredCategories": ["Dogs", "Cats"]
  }
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": 456,
    "username": "johndoe",
    "status": "pending_verification"
  }
}
```

#### PUT /api/v1/users/{userId}
**Description**: Update a user with optional state transition  
**Query Parameters**:
- `transition` (optional): Transition name (verify_user, deactivate_user, reactivate_user, suspend_user, unsuspend_user)

**Request Example** (Verify user):
```
PUT /api/v1/users/456?transition=verify_user

{
  "verificationToken": "VER_123456789"
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": 456,
    "status": "active",
    "emailVerified": true
  }
}
```

#### POST /api/v1/users/login
**Description**: User login endpoint

**Request Example**:
```json
{
  "username": "johndoe",
  "password": "SecurePassword123!"
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "token": "JWT_TOKEN_HERE",
    "user": {
      "id": 456,
      "username": "johndoe",
      "status": "active"
    }
  }
}
```

#### POST /api/v1/users/logout
**Description**: User logout endpoint

## 4. CategoryRoutes

**Class Name**: CategoryRoutes  
**Base Path**: `/api/v1/categories`  
**Description**: Manages all category-related API endpoints

### Endpoints

#### GET /api/v1/categories
**Description**: Get all categories

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Cats",
      "description": "Feline companions",
      "imageUrl": "https://example.com/cats.jpg",
      "status": "active",
      "displayOrder": 1
    }
  ]
}
```

#### POST /api/v1/categories
**Description**: Create a new category  
**Transition**: Triggers `create_category` transition (none → active)

**Request Example**:
```json
{
  "name": "Exotic Birds",
  "description": "Rare and exotic bird species",
  "imageUrl": "https://example.com/birds.jpg",
  "parentCategoryId": null,
  "displayOrder": 5
}
```

#### PUT /api/v1/categories/{categoryId}
**Description**: Update a category with optional state transition  
**Query Parameters**:
- `transition` (optional): Transition name (deactivate_category, reactivate_category)

## 5. TagRoutes

**Class Name**: TagRoutes  
**Base Path**: `/api/v1/tags`  
**Description**: Manages all tag-related API endpoints

### Endpoints

#### GET /api/v1/tags
**Description**: Get all tags

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "friendly",
      "description": "Pet is friendly with people",
      "color": "#4CAF50",
      "category": "behavior",
      "status": "active"
    }
  ]
}
```

#### POST /api/v1/tags
**Description**: Create a new tag  
**Transition**: Triggers `create_tag` transition (none → active)

**Request Example**:
```json
{
  "name": "hypoallergenic",
  "description": "Suitable for people with allergies",
  "color": "#2196F3",
  "category": "health"
}
```

#### PUT /api/v1/tags/{tagId}
**Description**: Update a tag with optional state transition  
**Query Parameters**:
- `transition` (optional): Transition name (deactivate_tag, reactivate_tag)

## Common Response Patterns

### Success Response
```json
{
  "success": true,
  "data": { /* entity data */ }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": ["Name is required", "Email format is invalid"]
  }
}
```

### Pagination Response
```json
{
  "success": true,
  "data": [ /* array of entities */ ],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "hasNext": true,
    "hasPrevious": false
  }
}
```

## Authentication & Authorization

- All endpoints except user registration and login require authentication
- Use JWT tokens for authentication
- Include `Authorization: Bearer <token>` header
- Users can only access their own orders and profile
- Admin users can access all resources

## Error Handling

- Return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Include detailed error messages for validation failures
- Log all errors for debugging purposes
- Handle workflow transition errors gracefully
