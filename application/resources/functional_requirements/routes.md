# Purrfect Pets - Routes Requirements

## Overview
This document defines the REST API routes for the Purrfect Pets API application. Each entity has its own routes class with CRUD operations and workflow transitions.

## PetRoutes

### 1. Create Pet
**Method**: POST  
**Path**: `/api/pets`  
**Description**: Create a new pet  
**Transition**: null (automatic INITIAL → DRAFT)

**Request Example**:
```json
{
    "name": "Fluffy",
    "category": {
        "id": 1,
        "name": "Cats"
    },
    "photoUrls": [
        "https://example.com/photos/fluffy1.jpg",
        "https://example.com/photos/fluffy2.jpg"
    ],
    "tags": [
        {
            "id": 1,
            "name": "friendly"
        },
        {
            "id": 2,
            "name": "indoor"
        }
    ],
    "description": "A beautiful Persian cat",
    "price": 500.00,
    "breed": "Persian",
    "age": 24,
    "gender": "FEMALE",
    "vaccinated": true,
    "neutered": true,
    "weight": 4.5,
    "color": "White"
}
```

**Response Example**:
```json
{
    "id": 123,
    "name": "Fluffy",
    "state": "DRAFT",
    "createdAt": "2024-01-15T10:30:00Z"
}
```

### 2. Get Pet by ID
**Method**: GET  
**Path**: `/api/pets/{petId}`  
**Description**: Retrieve a pet by ID

**Response Example**:
```json
{
    "id": 123,
    "name": "Fluffy",
    "state": "AVAILABLE",
    "category": {
        "id": 1,
        "name": "Cats"
    },
    "price": 500.00,
    "createdAt": "2024-01-15T10:30:00Z"
}
```

### 3. Update Pet
**Method**: PUT  
**Path**: `/api/pets/{petId}`  
**Query Parameter**: `transition` (optional)  
**Description**: Update pet information and optionally trigger state transition

**Request Example (with transition)**:
```json
{
    "name": "Fluffy Updated",
    "price": 550.00,
    "description": "Updated description",
    "transition": "DRAFT_TO_AVAILABLE"
}
```

**Request Example (without transition)**:
```json
{
    "name": "Fluffy Updated",
    "price": 550.00,
    "description": "Updated description",
    "transition": null
}
```

### 4. Get Pets by Status
**Method**: GET  
**Path**: `/api/pets/findByStatus`  
**Query Parameter**: `status` (AVAILABLE, PENDING, SOLD)  
**Description**: Find pets by status

### 5. Reserve Pet
**Method**: POST  
**Path**: `/api/pets/{petId}/reserve`  
**Description**: Reserve a pet for purchase  
**Transition**: AVAILABLE_TO_PENDING

**Request Example**:
```json
{
    "userId": 456,
    "quantity": 1,
    "deliveryAddress": "123 Main St, City, State 12345",
    "specialInstructions": "Please call before delivery",
    "transition": "AVAILABLE_TO_PENDING"
}
```

### 6. Complete Pet Sale
**Method**: POST  
**Path**: `/api/pets/{petId}/sell`  
**Description**: Complete the sale of a reserved pet  
**Transition**: PENDING_TO_SOLD

**Request Example**:
```json
{
    "paymentConfirmation": "PAY_123456789",
    "transition": "PENDING_TO_SOLD"
}
```

### 7. Release Pet Reservation
**Method**: POST  
**Path**: `/api/pets/{petId}/release`  
**Description**: Release pet from pending status  
**Transition**: PENDING_TO_AVAILABLE

**Request Example**:
```json
{
    "reason": "Customer cancelled order",
    "transition": "PENDING_TO_AVAILABLE"
}
```

## CategoryRoutes

### 1. Create Category
**Method**: POST  
**Path**: `/api/categories`  
**Description**: Create a new category  
**Transition**: null (automatic INITIAL → ACTIVE)

**Request Example**:
```json
{
    "name": "Dogs",
    "description": "All types of dogs",
    "imageUrl": "https://example.com/images/dogs.jpg"
}
```

**Response Example**:
```json
{
    "id": 1,
    "name": "Dogs",
    "state": "ACTIVE",
    "createdAt": "2024-01-15T10:30:00Z"
}
```

### 2. Get All Categories
**Method**: GET  
**Path**: `/api/categories`  
**Description**: Retrieve all categories

### 3. Update Category
**Method**: PUT  
**Path**: `/api/categories/{categoryId}`  
**Query Parameter**: `transition` (optional)  
**Description**: Update category information

**Request Example**:
```json
{
    "name": "Dogs Updated",
    "description": "Updated description",
    "transition": null
}
```

### 4. Deactivate Category
**Method**: POST  
**Path**: `/api/categories/{categoryId}/deactivate`  
**Description**: Deactivate a category  
**Transition**: ACTIVE_TO_INACTIVE

**Request Example**:
```json
{
    "reason": "Category no longer needed",
    "transition": "ACTIVE_TO_INACTIVE"
}
```

## TagRoutes

### 1. Create Tag
**Method**: POST  
**Path**: `/api/tags`  
**Description**: Create a new tag  
**Transition**: null (automatic INITIAL → ACTIVE)

**Request Example**:
```json
{
    "name": "friendly",
    "color": "#4CAF50",
    "description": "Pet is friendly with people"
}
```

### 2. Get All Tags
**Method**: GET  
**Path**: `/api/tags`  
**Description**: Retrieve all tags

### 3. Update Tag
**Method**: PUT
**Path**: `/api/tags/{tagId}`
**Query Parameter**: `transition` (optional)
**Description**: Update tag information

**Request Example**:
```json
{
    "name": "very-friendly",
    "color": "#2E7D32",
    "transition": null
}
```

## OrderRoutes

### 1. Create Order
**Method**: POST
**Path**: `/api/orders`
**Description**: Create a new order
**Transition**: null (automatic INITIAL → PLACED)

**Request Example**:
```json
{
    "userId": 456,
    "petId": 123,
    "quantity": 1,
    "deliveryAddress": "123 Main St, City, State 12345",
    "specialInstructions": "Please call before delivery",
    "paymentMethod": "CREDIT_CARD"
}
```

**Response Example**:
```json
{
    "id": 789,
    "userId": 456,
    "petId": 123,
    "state": "PLACED",
    "totalAmount": 500.00,
    "orderDate": "2024-01-15T10:30:00Z"
}
```

### 2. Get Order by ID
**Method**: GET
**Path**: `/api/orders/{orderId}`
**Description**: Retrieve an order by ID

### 3. Update Order
**Method**: PUT
**Path**: `/api/orders/{orderId}`
**Query Parameter**: `transition` (optional)
**Description**: Update order information

**Request Example**:
```json
{
    "deliveryAddress": "456 Oak Ave, City, State 12345",
    "specialInstructions": "Updated instructions",
    "transition": null
}
```

### 4. Confirm Order
**Method**: POST
**Path**: `/api/orders/{orderId}/confirm`
**Description**: Confirm order with payment
**Transition**: PLACED_TO_CONFIRMED

**Request Example**:
```json
{
    "paymentDetails": {
        "cardNumber": "****-****-****-1234",
        "expiryDate": "12/25",
        "cvv": "***"
    },
    "transition": "PLACED_TO_CONFIRMED"
}
```

### 5. Process Order
**Method**: POST
**Path**: `/api/orders/{orderId}/process`
**Description**: Begin processing the order
**Transition**: CONFIRMED_TO_PROCESSING

**Request Example**:
```json
{
    "assignedTo": "fulfillment-team-1",
    "transition": "CONFIRMED_TO_PROCESSING"
}
```

### 6. Ship Order
**Method**: POST
**Path**: `/api/orders/{orderId}/ship`
**Description**: Ship the order
**Transition**: PROCESSING_TO_SHIPPED

**Request Example**:
```json
{
    "trackingNumber": "TRACK123456789",
    "carrier": "PetExpress",
    "estimatedDelivery": "2024-01-20T15:00:00Z",
    "transition": "PROCESSING_TO_SHIPPED"
}
```

### 7. Mark Order Delivered
**Method**: POST
**Path**: `/api/orders/{orderId}/deliver`
**Description**: Mark order as delivered
**Transition**: SHIPPED_TO_DELIVERED

**Request Example**:
```json
{
    "deliveryConfirmation": "DELIVERED_123456",
    "deliveredAt": "2024-01-20T14:30:00Z",
    "transition": "SHIPPED_TO_DELIVERED"
}
```

### 8. Cancel Order
**Method**: POST
**Path**: `/api/orders/{orderId}/cancel`
**Description**: Cancel an order
**Transition**: PLACED_TO_CANCELLED or CONFIRMED_TO_CANCELLED

**Request Example**:
```json
{
    "cancellationReason": "Customer requested cancellation",
    "refundAmount": 500.00,
    "transition": "CONFIRMED_TO_CANCELLED"
}
```

### 9. Return Order
**Method**: POST
**Path**: `/api/orders/{orderId}/return`
**Description**: Process order return
**Transition**: DELIVERED_TO_RETURNED

**Request Example**:
```json
{
    "returnReason": "Pet not as described",
    "pickupAddress": "123 Main St, City, State 12345",
    "refundAmount": 500.00,
    "transition": "DELIVERED_TO_RETURNED"
}
```

### 10. Get Orders by User
**Method**: GET
**Path**: `/api/orders/user/{userId}`
**Description**: Get all orders for a specific user

## UserRoutes

### 1. Register User
**Method**: POST
**Path**: `/api/users/register`
**Description**: Register a new user
**Transition**: null (automatic INITIAL → REGISTERED)

**Request Example**:
```json
{
    "username": "johndoe",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "password": "SecurePassword123!",
    "phone": "+1-555-123-4567",
    "address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zipCode": "12345",
    "country": "USA",
    "dateOfBirth": "1990-05-15",
    "preferredPetType": "Dogs"
}
```

**Response Example**:
```json
{
    "id": 456,
    "username": "johndoe",
    "email": "john.doe@example.com",
    "state": "REGISTERED",
    "createdAt": "2024-01-15T10:30:00Z"
}
```

### 2. Verify User Email
**Method**: POST
**Path**: `/api/users/{userId}/verify`
**Description**: Verify user email address
**Transition**: REGISTERED_TO_VERIFIED

**Request Example**:
```json
{
    "verificationToken": "VER_TOKEN_123456789",
    "transition": "REGISTERED_TO_VERIFIED"
}
```

### 3. Get User by ID
**Method**: GET
**Path**: `/api/users/{userId}`
**Description**: Retrieve a user by ID

**Response Example**:
```json
{
    "id": 456,
    "username": "johndoe",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "state": "ACTIVE",
    "isActive": true,
    "emailVerified": true
}
```

### 4. Update User
**Method**: PUT
**Path**: `/api/users/{userId}`
**Query Parameter**: `transition` (optional)
**Description**: Update user information

**Request Example**:
```json
{
    "firstName": "John Updated",
    "phone": "+1-555-987-6543",
    "address": "456 Oak Ave",
    "preferredPetType": "Cats",
    "transition": null
}
```

### 5. Suspend User
**Method**: POST
**Path**: `/api/users/{userId}/suspend`
**Description**: Suspend a user account
**Transition**: ACTIVE_TO_SUSPENDED

**Request Example**:
```json
{
    "suspensionReason": "POLICY_VIOLATION",
    "notes": "Violated terms of service",
    "transition": "ACTIVE_TO_SUSPENDED"
}
```

### 6. Reactivate User
**Method**: POST
**Path**: `/api/users/{userId}/reactivate`
**Description**: Reactivate a suspended or deactivated user
**Transition**: SUSPENDED_TO_ACTIVE or DEACTIVATED_TO_ACTIVE

**Request Example**:
```json
{
    "resolutionData": {
        "paymentResolved": true,
        "acknowledgment": true,
        "investigationComplete": true
    },
    "transition": "SUSPENDED_TO_ACTIVE"
}
```

### 7. Deactivate User
**Method**: POST
**Path**: `/api/users/{userId}/deactivate`
**Description**: Deactivate a user account
**Transition**: ACTIVE_TO_DEACTIVATED

**Request Example**:
```json
{
    "reason": "User requested account deactivation",
    "transition": "ACTIVE_TO_DEACTIVATED"
}
```

### 8. User Login
**Method**: POST
**Path**: `/api/users/login`
**Description**: Authenticate user login

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
    "token": "JWT_TOKEN_HERE",
    "user": {
        "id": 456,
        "username": "johndoe",
        "state": "ACTIVE"
    },
    "expiresAt": "2024-01-16T10:30:00Z"
}
```

### 9. Get User Orders
**Method**: GET
**Path**: `/api/users/{userId}/orders`
**Description**: Get all orders for a user

### 10. Update User Password
**Method**: PUT
**Path**: `/api/users/{userId}/password`
**Description**: Update user password

**Request Example**:
```json
{
    "currentPassword": "OldPassword123!",
    "newPassword": "NewSecurePassword456!"
}
```

## Route Notes

1. **Authentication**: Most routes require authentication except for registration, login, and public pet browsing.

2. **Authorization**: Users can only access their own data unless they have admin privileges.

3. **Validation**: All input data should be validated before processing.

4. **Error Handling**: All routes should return appropriate HTTP status codes and error messages.

5. **Pagination**: List endpoints should support pagination parameters (page, size, sort).

6. **Filtering**: Search endpoints should support filtering by various criteria.

7. **Transition Parameters**: Update endpoints with transition parameters should validate that the current entity state allows the specified transition.

8. **Response Format**: All responses should follow a consistent JSON format with appropriate metadata.
