# Purrfect Pets API - Controller Requirements

## Overview
This document defines the REST API controllers for the Purrfect Pets API. Each entity has its own routes class with CRUD operations and workflow transitions.

## 1. PetRoutes

**Class Name**: PetRoutes
**Base URL**: `/api/pets`

### Endpoints

#### GET /api/pets
**Description**: List all pets with optional filtering
**Parameters**:
- `status` (query, optional): Filter by availability status (available, pending, sold)
- `category_id` (query, optional): Filter by category ID
- `min_price` (query, optional): Minimum price filter
- `max_price` (query, optional): Maximum price filter
- `page` (query, optional): Page number (default: 1)
- `limit` (query, optional): Items per page (default: 20)

**Response Example**:
```json
{
  "pets": [
    {
      "id": "pet-123",
      "name": "Fluffy",
      "category_id": "cat-001",
      "price": 299.99,
      "status": "available",
      "photo_urls": ["https://example.com/fluffy1.jpg"],
      "breed": "Persian",
      "age": 12,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

#### GET /api/pets/{pet_id}
**Description**: Get specific pet by ID

**Response Example**:
```json
{
  "id": "pet-123",
  "name": "Fluffy",
  "category_id": "cat-001",
  "photo_urls": ["https://example.com/fluffy1.jpg", "https://example.com/fluffy2.jpg"],
  "tags": ["friendly", "indoor"],
  "breed": "Persian",
  "age": 12,
  "weight": 4.5,
  "color": "white",
  "gender": "female",
  "vaccination_status": true,
  "microchip_id": "123456789012345",
  "description": "Beautiful Persian cat, very friendly and loves attention",
  "price": 299.99,
  "status": "available",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### POST /api/pets
**Description**: Create a new pet
**Request Example**:
```json
{
  "name": "Buddy",
  "category_id": "dog-001",
  "photo_urls": ["https://example.com/buddy1.jpg"],
  "tags": ["playful", "trained"],
  "breed": "Golden Retriever",
  "age": 24,
  "weight": 25.0,
  "color": "golden",
  "gender": "male",
  "vaccination_status": true,
  "microchip_id": "987654321098765",
  "description": "Friendly Golden Retriever, great with kids",
  "price": 599.99
}
```

**Response Example**:
```json
{
  "id": "pet-124",
  "message": "Pet created successfully",
  "status": "available"
}
```

#### PUT /api/pets/{pet_id}
**Description**: Update pet information and optionally trigger workflow transition
**Parameters**:
- `transition` (query, optional): Workflow transition name

**Request Example**:
```json
{
  "name": "Buddy Updated",
  "price": 649.99,
  "description": "Updated description",
  "transition": "reserve_pet"
}
```

**Response Example**:
```json
{
  "id": "pet-124",
  "message": "Pet updated successfully",
  "status": "pending"
}
```

#### DELETE /api/pets/{pet_id}
**Description**: Delete pet (soft delete)

**Response Example**:
```json
{
  "message": "Pet deleted successfully"
}
```

## 2. CategoryRoutes

**Class Name**: CategoryRoutes
**Base URL**: `/api/categories`

### Endpoints

#### GET /api/categories
**Description**: List all categories
**Parameters**:
- `status` (query, optional): Filter by status (active, inactive)
- `featured` (query, optional): Filter by featured status (true, false)

**Response Example**:
```json
{
  "categories": [
    {
      "id": "cat-001",
      "name": "Cats",
      "description": "Feline companions",
      "status": "active",
      "is_featured": true,
      "pet_count": 15,
      "display_order": 1
    }
  ]
}
```

#### GET /api/categories/{category_id}
**Description**: Get specific category by ID

#### POST /api/categories
**Description**: Create a new category
**Request Example**:
```json
{
  "name": "Birds",
  "description": "Feathered friends",
  "icon_url": "https://example.com/bird-icon.png",
  "display_order": 3,
  "is_featured": false
}
```

#### PUT /api/categories/{category_id}
**Description**: Update category and optionally trigger workflow transition
**Parameters**:
- `transition` (query, optional): Workflow transition name (deactivate_category, reactivate_category)

**Request Example**:
```json
{
  "name": "Birds Updated",
  "description": "Updated description",
  "transition": "deactivate_category"
}
```

#### DELETE /api/categories/{category_id}
**Description**: Delete category

## 3. CustomerRoutes

**Class Name**: CustomerRoutes
**Base URL**: `/api/customers`

### Endpoints

#### GET /api/customers
**Description**: List all customers (admin only)
**Parameters**:
- `status` (query, optional): Filter by status (registered, verified, suspended, deleted)
- `page` (query, optional): Page number
- `limit` (query, optional): Items per page

#### GET /api/customers/{customer_id}
**Description**: Get specific customer by ID

#### POST /api/customers
**Description**: Register a new customer
**Request Example**:
```json
{
  "username": "johndoe123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1-555-0123",
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip_code": "12345",
    "country": "USA"
  },
  "date_of_birth": "1990-05-15",
  "preferences": {
    "preferred_pet_types": ["dogs", "cats"],
    "newsletter_subscription": true
  }
}
```

**Response Example**:
```json
{
  "id": "customer-123",
  "message": "Customer registered successfully. Please check your email for verification.",
  "status": "registered"
}
```

#### PUT /api/customers/{customer_id}
**Description**: Update customer information and optionally trigger workflow transition
**Parameters**:
- `transition` (query, optional): Workflow transition name (verify_email, suspend_account, reactivate_account, delete_account)

**Request Example**:
```json
{
  "first_name": "John Updated",
  "phone": "+1-555-0124",
  "transition": "verify_email",
  "verification_token": "abc123def456"
}
```

#### DELETE /api/customers/{customer_id}
**Description**: Delete customer account

## 4. OrderRoutes

**Class Name**: OrderRoutes
**Base URL**: `/api/orders`

### Endpoints

#### GET /api/orders
**Description**: List orders
**Parameters**:
- `customer_id` (query, optional): Filter by customer ID
- `status` (query, optional): Filter by status
- `page` (query, optional): Page number
- `limit` (query, optional): Items per page

#### GET /api/orders/{order_id}
**Description**: Get specific order by ID

**Response Example**:
```json
{
  "id": "order-123",
  "customer_id": "customer-123",
  "order_date": "2024-01-15T14:30:00Z",
  "total_amount": 899.98,
  "status": "placed",
  "shipping_address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip_code": "12345",
    "country": "USA"
  },
  "payment_method": "credit_card",
  "items": [
    {
      "id": "item-001",
      "pet_id": "pet-123",
      "pet_name": "Fluffy",
      "quantity": 1,
      "unit_price": 299.99,
      "subtotal": 299.99
    },
    {
      "id": "item-002",
      "pet_id": "pet-124",
      "pet_name": "Buddy",
      "quantity": 1,
      "unit_price": 599.99,
      "subtotal": 599.99
    }
  ]
}
```

#### POST /api/orders
**Description**: Place a new order
**Request Example**:
```json
{
  "customer_id": "customer-123",
  "shipping_address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip_code": "12345",
    "country": "USA"
  },
  "payment_method": "credit_card",
  "notes": "Please handle with care",
  "items": [
    {
      "pet_id": "pet-123",
      "quantity": 1,
      "special_instructions": "Include favorite toy"
    }
  ]
}
```

**Response Example**:
```json
{
  "id": "order-123",
  "message": "Order placed successfully",
  "status": "placed",
  "total_amount": 299.99
}
```

#### PUT /api/orders/{order_id}
**Description**: Update order and optionally trigger workflow transition
**Parameters**:
- `transition` (query, required for state changes): Workflow transition name (approve_order, prepare_order, ship_order, deliver_order, cancel_placed_order, cancel_approved_order)

**Request Example**:
```json
{
  "notes": "Updated delivery instructions",
  "transition": "approve_order",
  "payment_verified": true,
  "payment_reference": "PAY-123456789"
}
```

**Response Example**:
```json
{
  "id": "order-123",
  "message": "Order approved successfully",
  "status": "approved"
}
```

#### DELETE /api/orders/{order_id}
**Description**: Cancel order

## 5. OrderItemRoutes

**Class Name**: OrderItemRoutes
**Base URL**: `/api/order-items`

### Endpoints

#### GET /api/order-items
**Description**: List order items
**Parameters**:
- `order_id` (query, optional): Filter by order ID
- `pet_id` (query, optional): Filter by pet ID

#### GET /api/order-items/{item_id}
**Description**: Get specific order item by ID

#### PUT /api/order-items/{item_id}
**Description**: Update order item and optionally trigger workflow transition
**Parameters**:
- `transition` (query, optional): Workflow transition name (confirm_item, prepare_item, ship_item, deliver_item)

**Request Example**:
```json
{
  "special_instructions": "Handle with extra care",
  "transition": "confirm_item"
}
```

**Response Example**:
```json
{
  "id": "item-001",
  "message": "Order item confirmed successfully",
  "status": "confirmed"
}
```

## API Standards

### Authentication
- All endpoints require authentication except public pet listings
- Use JWT tokens for authentication
- Admin endpoints require admin role

### Error Responses
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional error details"
}
```

### Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

### Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```
