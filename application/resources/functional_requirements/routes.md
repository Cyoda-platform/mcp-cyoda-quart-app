# Purrfect Pets API - Routes Requirements

## Overview
This document defines the REST API routes for the Purrfect Pets API system, including request/response examples for each entity.

## PetRoutes

### GET /api/pets
**Description**: Get all pets with optional filtering  
**Parameters**: 
- `status` (optional): Filter by pet status (available, reserved, adopted, medical_hold, unavailable)
- `category` (optional): Filter by category ID
- `page` (optional): Page number for pagination (default: 0)
- `size` (optional): Page size (default: 20)

**Request Example**:
```
GET /api/pets?status=available&category=1&page=0&size=10
```

**Response Example**:
```json
{
  "content": [
    {
      "id": 1,
      "name": "Buddy",
      "categoryId": 1,
      "breed": "Golden Retriever",
      "age": 24,
      "weight": 25.5,
      "color": "Golden",
      "price": 500.00,
      "state": "AVAILABLE"
    }
  ],
  "totalElements": 1,
  "totalPages": 1,
  "size": 10,
  "number": 0
}
```

### GET /api/pets/{id}
**Description**: Get pet by ID

**Request Example**:
```
GET /api/pets/1
```

**Response Example**:
```json
{
  "id": 1,
  "name": "Buddy",
  "categoryId": 1,
  "photoUrls": ["https://example.com/buddy1.jpg"],
  "tags": ["friendly", "trained"],
  "breed": "Golden Retriever",
  "age": 24,
  "weight": 25.5,
  "color": "Golden",
  "description": "Friendly and well-trained dog",
  "price": 500.00,
  "vaccinated": true,
  "neutered": true,
  "microchipped": true,
  "state": "AVAILABLE",
  "createdAt": "2024-01-15T10:30:00",
  "updatedAt": "2024-01-15T10:30:00"
}
```

### POST /api/pets
**Description**: Create a new pet

**Request Example**:
```json
{
  "name": "Max",
  "categoryId": 1,
  "photoUrls": ["https://example.com/max1.jpg"],
  "tags": ["playful", "young"],
  "breed": "Labrador",
  "age": 12,
  "weight": 15.0,
  "color": "Black",
  "description": "Playful young labrador",
  "price": 400.00,
  "vaccinated": true,
  "neutered": false,
  "microchipped": true
}
```

**Response Example**:
```json
{
  "id": 2,
  "name": "Max",
  "state": "AVAILABLE",
  "createdAt": "2024-01-15T11:00:00"
}
```

### PUT /api/pets/{id}
**Description**: Update pet information  
**Parameters**: 
- `transitionName` (optional): Transition to trigger (reserve, adopt, medical_hold, clear_medical, make_unavailable, make_available, cancel_reservation)

**Request Example**:
```json
{
  "name": "Max Updated",
  "description": "Updated description",
  "price": 450.00,
  "transitionName": "reserve",
  "ownerId": 1
}
```

**Response Example**:
```json
{
  "id": 2,
  "name": "Max Updated",
  "state": "RESERVED",
  "updatedAt": "2024-01-15T12:00:00"
}
```

### DELETE /api/pets/{id}
**Description**: Delete a pet (soft delete)

## CategoryRoutes

### GET /api/categories
**Description**: Get all categories

**Request Example**:
```
GET /api/categories
```

**Response Example**:
```json
[
  {
    "id": 1,
    "name": "Dogs",
    "description": "All dog breeds",
    "imageUrl": "https://example.com/dogs.jpg",
    "state": "ACTIVE"
  },
  {
    "id": 2,
    "name": "Cats",
    "description": "All cat breeds",
    "imageUrl": "https://example.com/cats.jpg",
    "state": "ACTIVE"
  }
]
```

### GET /api/categories/{id}
**Description**: Get category by ID

**Request Example**:
```
GET /api/categories/1
```

**Response Example**:
```json
{
  "id": 1,
  "name": "Dogs",
  "description": "All dog breeds",
  "imageUrl": "https://example.com/dogs.jpg",
  "state": "ACTIVE",
  "createdAt": "2024-01-01T00:00:00",
  "updatedAt": "2024-01-01T00:00:00"
}
```

### POST /api/categories
**Description**: Create a new category

**Request Example**:
```json
{
  "name": "Birds",
  "description": "All bird species",
  "imageUrl": "https://example.com/birds.jpg"
}
```

**Response Example**:
```json
{
  "id": 3,
  "name": "Birds",
  "state": "ACTIVE",
  "createdAt": "2024-01-15T11:30:00"
}
```

### PUT /api/categories/{id}
**Description**: Update category  
**Parameters**: 
- `transitionName` (optional): Transition to trigger (deactivate, activate)

**Request Example**:
```json
{
  "description": "Updated description for all bird species",
  "transitionName": "deactivate"
}
```

**Response Example**:
```json
{
  "id": 3,
  "state": "INACTIVE",
  "updatedAt": "2024-01-15T12:30:00"
}
```

## OwnerRoutes

### GET /api/owners
**Description**: Get all owners with optional filtering  
**Parameters**: 
- `status` (optional): Filter by owner status
- `email` (optional): Filter by email
- `page` (optional): Page number for pagination
- `size` (optional): Page size

**Request Example**:
```
GET /api/owners?status=approved&page=0&size=10
```

**Response Example**:
```json
{
  "content": [
    {
      "id": 1,
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "state": "APPROVED"
    }
  ],
  "totalElements": 1
}
```

### GET /api/owners/{id}
**Description**: Get owner by ID

**Request Example**:
```
GET /api/owners/1
```

**Response Example**:
```json
{
  "id": 1,
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "Anytown",
  "state": "CA",
  "zipCode": "12345",
  "country": "USA",
  "dateOfBirth": "1985-05-15",
  "occupation": "Software Engineer",
  "housingType": "house",
  "hasYard": true,
  "hasOtherPets": false,
  "experienceLevel": "intermediate",
  "preferredContactMethod": "email",
  "state": "APPROVED",
  "createdAt": "2024-01-10T09:00:00"
}
```

### POST /api/owners
**Description**: Register a new owner

**Request Example**:
```json
{
  "firstName": "Jane",
  "lastName": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1987654321",
  "address": "456 Oak Ave",
  "city": "Somewhere",
  "state": "NY",
  "zipCode": "54321",
  "country": "USA",
  "dateOfBirth": "1990-08-20",
  "occupation": "Teacher",
  "housingType": "apartment",
  "hasYard": false,
  "hasOtherPets": true,
  "experienceLevel": "beginner",
  "preferredContactMethod": "phone"
}
```

**Response Example**:
```json
{
  "id": 2,
  "firstName": "Jane",
  "lastName": "Smith",
  "email": "jane.smith@example.com",
  "state": "REGISTERED",
  "createdAt": "2024-01-15T13:00:00"
}
```

### PUT /api/owners/{id}
**Description**: Update owner information  
**Parameters**: 
- `transitionName` (optional): Transition to trigger (verify, approve, suspend, reinstate, deactivate, reactivate)

**Request Example**:
```json
{
  "phone": "+1987654322",
  "address": "456 Oak Ave Apt 2B",
  "transitionName": "verify"
}
```

**Response Example**:
```json
{
  "id": 2,
  "state": "VERIFIED",
  "updatedAt": "2024-01-15T14:00:00"
}
```

## OrderRoutes

### GET /api/orders
**Description**: Get all orders with optional filtering  
**Parameters**: 
- `ownerId` (optional): Filter by owner ID
- `status` (optional): Filter by order status
- `page` (optional): Page number for pagination
- `size` (optional): Page size

**Request Example**:
```
GET /api/orders?ownerId=1&status=confirmed&page=0&size=10
```

**Response Example**:
```json
{
  "content": [
    {
      "id": 1,
      "ownerId": 1,
      "orderDate": "2024-01-15T10:00:00",
      "totalAmount": 500.00,
      "state": "CONFIRMED"
    }
  ]
}
```

### GET /api/orders/{id}
**Description**: Get order by ID

**Request Example**:
```
GET /api/orders/1
```

**Response Example**:
```json
{
  "id": 1,
  "ownerId": 1,
  "orderDate": "2024-01-15T10:00:00",
  "totalAmount": 500.00,
  "shippingAddress": "123 Main St, Anytown, CA 12345",
  "paymentMethod": "credit_card",
  "state": "CONFIRMED",
  "items": [
    {
      "id": 1,
      "petId": 1,
      "productName": "Golden Retriever - Buddy",
      "quantity": 1,
      "unitPrice": 500.00,
      "totalPrice": 500.00
    }
  ]
}
```

### POST /api/orders
**Description**: Create a new order

**Request Example**:
```json
{
  "ownerId": 1,
  "shippingAddress": "123 Main St, Anytown, CA 12345",
  "paymentMethod": "credit_card",
  "items": [
    {
      "petId": 1,
      "productName": "Golden Retriever - Buddy",
      "quantity": 1,
      "unitPrice": 500.00
    }
  ],
  "paymentDetails": {
    "cardNumber": "****-****-****-1234",
    "expiryDate": "12/25",
    "cvv": "123"
  }
}
```

**Response Example**:
```json
{
  "id": 1,
  "ownerId": 1,
  "totalAmount": 500.00,
  "state": "PENDING",
  "createdAt": "2024-01-15T10:00:00"
}
```

### PUT /api/orders/{id}
**Description**: Update order  
**Parameters**: 
- `transitionName` (optional): Transition to trigger (confirm, process, ship, deliver, cancel, refund)

**Request Example**:
```json
{
  "transitionName": "confirm",
  "paymentConfirmationId": "PAY123456789"
}
```

**Response Example**:
```json
{
  "id": 1,
  "state": "CONFIRMED",
  "updatedAt": "2024-01-15T10:30:00"
}
```

## AdoptionApplicationRoutes

### GET /api/adoption-applications
**Description**: Get all adoption applications with optional filtering  
**Parameters**: 
- `ownerId` (optional): Filter by owner ID
- `petId` (optional): Filter by pet ID
- `status` (optional): Filter by application status
- `page` (optional): Page number for pagination
- `size` (optional): Page size

**Request Example**:
```
GET /api/adoption-applications?ownerId=1&status=under_review&page=0&size=10
```

**Response Example**:
```json
{
  "content": [
    {
      "id": 1,
      "ownerId": 1,
      "petId": 1,
      "applicationDate": "2024-01-15T09:00:00",
      "state": "UNDER_REVIEW"
    }
  ]
}
```

### GET /api/adoption-applications/{id}
**Description**: Get adoption application by ID

**Request Example**:
```
GET /api/adoption-applications/1
```

**Response Example**:
```json
{
  "id": 1,
  "ownerId": 1,
  "petId": 1,
  "applicationDate": "2024-01-15T09:00:00",
  "reasonForAdoption": "Looking for a family companion",
  "previousPetExperience": "Had dogs for 10 years",
  "livingArrangement": "House with large yard",
  "workSchedule": "9-5 weekdays, home evenings and weekends",
  "veterinarianContact": "Dr. Smith, Pet Clinic, 555-0123",
  "references": ["Alice Johnson: 555-0111", "Bob Wilson: 555-0222"],
  "agreedToTerms": true,
  "state": "UNDER_REVIEW",
  "createdAt": "2024-01-15T09:00:00"
}
```

### POST /api/adoption-applications
**Description**: Submit a new adoption application

**Request Example**:
```json
{
  "ownerId": 1,
  "petId": 1,
  "reasonForAdoption": "Looking for a family companion",
  "previousPetExperience": "Had dogs for 10 years",
  "livingArrangement": "House with large yard",
  "workSchedule": "9-5 weekdays, home evenings and weekends",
  "veterinarianContact": "Dr. Smith, Pet Clinic, 555-0123",
  "references": ["Alice Johnson: 555-0111", "Bob Wilson: 555-0222"],
  "agreedToTerms": true
}
```

**Response Example**:
```json
{
  "id": 1,
  "ownerId": 1,
  "petId": 1,
  "state": "SUBMITTED",
  "createdAt": "2024-01-15T09:00:00"
}
```

### PUT /api/adoption-applications/{id}
**Description**: Update adoption application  
**Parameters**: 
- `transitionName` (optional): Transition to trigger (review, approve, reject, withdraw)

**Request Example**:
```json
{
  "transitionName": "approve",
  "reviewNotes": "Excellent candidate, all references checked",
  "reviewedBy": "Staff Member 1"
}
```

**Response Example**:
```json
{
  "id": 1,
  "state": "APPROVED",
  "reviewedBy": "Staff Member 1",
  "updatedAt": "2024-01-15T15:00:00"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Bad Request",
  "message": "Invalid input data",
  "timestamp": "2024-01-15T10:00:00",
  "path": "/api/pets"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "message": "Pet with ID 999 not found",
  "timestamp": "2024-01-15T10:00:00",
  "path": "/api/pets/999"
}
```

### 409 Conflict
```json
{
  "error": "Conflict",
  "message": "Pet is not available for reservation",
  "timestamp": "2024-01-15T10:00:00",
  "path": "/api/pets/1"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred",
  "timestamp": "2024-01-15T10:00:00",
  "path": "/api/pets"
}
```
