# Entities Specification for Purrfect Pets API

## Overview
This document defines the entities for the Purrfect Pets API application, including their attributes and relationships.

## Entities

### 1. Pet Entity
**Description**: Represents a pet in the store inventory

**Attributes**:
- `id` (Long): Unique identifier for the pet
- `name` (String): Name of the pet (required)
- `category` (Category): Category the pet belongs to
- `photoUrls` (List<String>): List of photo URLs for the pet (required)
- `tags` (List<Tag>): List of tags associated with the pet
- `description` (String): Description of the pet
- `price` (BigDecimal): Price of the pet
- `birthDate` (LocalDate): Birth date of the pet
- `breed` (String): Breed of the pet
- `weight` (Double): Weight of the pet in kg
- `vaccinated` (Boolean): Whether the pet is vaccinated
- `neutered` (Boolean): Whether the pet is neutered/spayed

**State Management**:
- Entity state is managed internally via `entity.meta.state`
- States: AVAILABLE, PENDING, SOLD, RESERVED, UNAVAILABLE

**Relationships**:
- Many-to-One with Category
- Many-to-Many with Tag
- One-to-Many with Order (through OrderItem)

### 2. Category Entity
**Description**: Represents a category of pets (e.g., Dogs, Cats, Birds)

**Attributes**:
- `id` (Long): Unique identifier for the category
- `name` (String): Name of the category (required)
- `description` (String): Description of the category

**State Management**:
- Entity state is managed internally via `entity.meta.state`
- States: ACTIVE, INACTIVE

**Relationships**:
- One-to-Many with Pet

### 3. Tag Entity
**Description**: Represents tags for categorizing pets (e.g., friendly, trained, hypoallergenic)

**Attributes**:
- `id` (Long): Unique identifier for the tag
- `name` (String): Name of the tag (required)
- `color` (String): Color code for the tag display

**State Management**:
- Entity state is managed internally via `entity.meta.state`
- States: ACTIVE, INACTIVE

**Relationships**:
- Many-to-Many with Pet

### 4. User Entity
**Description**: Represents users of the system (customers and staff)

**Attributes**:
- `id` (Long): Unique identifier for the user
- `username` (String): Username for login (required, unique)
- `firstName` (String): First name of the user
- `lastName` (String): Last name of the user
- `email` (String): Email address (required, unique)
- `password` (String): Encrypted password (required)
- `phone` (String): Phone number
- `address` (Address): User's address
- `role` (UserRole): Role of the user (CUSTOMER, STAFF, ADMIN)
- `registrationDate` (LocalDateTime): When the user registered

**State Management**:
- Entity state is managed internally via `entity.meta.state`
- States: ACTIVE, INACTIVE, SUSPENDED, PENDING_VERIFICATION

**Relationships**:
- One-to-Many with Order
- One-to-One with Address

### 5. Order Entity
**Description**: Represents an order placed by a customer

**Attributes**:
- `id` (Long): Unique identifier for the order
- `userId` (Long): ID of the user who placed the order (required)
- `orderDate` (LocalDateTime): Date and time when the order was placed
- `shipDate` (LocalDateTime): Date when the order was shipped
- `totalAmount` (BigDecimal): Total amount of the order
- `shippingAddress` (Address): Shipping address for the order
- `paymentMethod` (String): Payment method used
- `notes` (String): Additional notes for the order

**State Management**:
- Entity state is managed internally via `entity.meta.state`
- States: PLACED, APPROVED, DELIVERED, CANCELLED

**Relationships**:
- Many-to-One with User
- One-to-Many with OrderItem
- One-to-One with Address (shipping address)

### 6. OrderItem Entity
**Description**: Represents individual items within an order

**Attributes**:
- `id` (Long): Unique identifier for the order item
- `orderId` (Long): ID of the order this item belongs to (required)
- `petId` (Long): ID of the pet being ordered (required)
- `quantity` (Integer): Quantity of the pet (usually 1 for pets)
- `unitPrice` (BigDecimal): Price per unit at the time of order
- `totalPrice` (BigDecimal): Total price for this item (quantity * unitPrice)

**State Management**:
- Entity state is managed internally via `entity.meta.state`
- States: PENDING, CONFIRMED, DELIVERED, CANCELLED

**Relationships**:
- Many-to-One with Order
- Many-to-One with Pet

### 7. Address Entity
**Description**: Represents address information

**Attributes**:
- `id` (Long): Unique identifier for the address
- `street` (String): Street address
- `city` (String): City name
- `state` (String): State or province
- `zipCode` (String): ZIP or postal code
- `country` (String): Country name

**State Management**:
- Entity state is managed internally via `entity.meta.state`
- States: ACTIVE, INACTIVE

**Relationships**:
- One-to-One with User
- One-to-Many with Order (as shipping address)

## Enumerations

### UserRole
- CUSTOMER: Regular customer who can browse and purchase pets
- STAFF: Store staff who can manage inventory and orders
- ADMIN: Administrator with full system access

## Entity Relationships Summary

```
User (1) -----> (M) Order
User (1) -----> (1) Address
Order (1) -----> (M) OrderItem
Order (1) -----> (1) Address (shipping)
OrderItem (M) -----> (1) Pet
Pet (M) -----> (1) Category
Pet (M) -----> (M) Tag
```

## Notes

- All entities use `entity.meta.state` for state management
- State transitions are handled automatically by the workflow system
- Entity IDs are auto-generated Long values
- All timestamps use LocalDateTime for consistency
- Prices use BigDecimal for precision
- Required fields are marked as (required)
- Unique constraints are marked as (unique)
