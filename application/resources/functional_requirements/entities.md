# Purrfect Pets - Entity Requirements

## Overview
This document defines the entities for the Purrfect Pets API application, including their attributes and relationships.

## Entities

### 1. Pet Entity
**Description**: Represents a pet available in the store

**Attributes**:
- `id` (Long): Unique identifier for the pet
- `name` (String): Name of the pet (required)
- `category` (Category): Category the pet belongs to
- `photoUrls` (List<String>): List of photo URLs for the pet (required)
- `tags` (List<Tag>): List of tags associated with the pet
- `description` (String): Description of the pet
- `price` (BigDecimal): Price of the pet
- `breed` (String): Breed of the pet
- `age` (Integer): Age of the pet in months
- `gender` (String): Gender of the pet (MALE, FEMALE, UNKNOWN)
- `vaccinated` (Boolean): Whether the pet is vaccinated
- `neutered` (Boolean): Whether the pet is neutered/spayed
- `weight` (BigDecimal): Weight of the pet in kg
- `color` (String): Primary color of the pet
- `createdAt` (LocalDateTime): When the pet was added to the system
- `updatedAt` (LocalDateTime): When the pet was last updated

**Entity State**: Uses `meta.state` to track pet lifecycle (not included in schema)

**Relationships**:
- Many-to-One with Category
- Many-to-Many with Tag
- One-to-Many with OrderItem (through Order)

### 2. Category Entity
**Description**: Represents a category of pets

**Attributes**:
- `id` (Long): Unique identifier for the category
- `name` (String): Name of the category (required)
- `description` (String): Description of the category
- `imageUrl` (String): Image URL for the category
- `createdAt` (LocalDateTime): When the category was created
- `updatedAt` (LocalDateTime): When the category was last updated

**Entity State**: Uses `meta.state` to track category lifecycle (not included in schema)

**Relationships**:
- One-to-Many with Pet

### 3. Tag Entity
**Description**: Represents tags that can be associated with pets

**Attributes**:
- `id` (Long): Unique identifier for the tag
- `name` (String): Name of the tag (required)
- `color` (String): Color code for the tag display
- `description` (String): Description of the tag
- `createdAt` (LocalDateTime): When the tag was created

**Entity State**: Uses `meta.state` to track tag lifecycle (not included in schema)

**Relationships**:
- Many-to-Many with Pet

### 4. Order Entity
**Description**: Represents a customer order for pets

**Attributes**:
- `id` (Long): Unique identifier for the order
- `userId` (Long): ID of the user who placed the order (required)
- `petId` (Long): ID of the pet being ordered (required)
- `quantity` (Integer): Quantity of pets ordered (default: 1)
- `totalAmount` (BigDecimal): Total amount for the order
- `orderDate` (LocalDateTime): When the order was placed
- `shipDate` (LocalDateTime): When the order was shipped
- `deliveryAddress` (String): Delivery address for the order
- `specialInstructions` (String): Special instructions for the order
- `paymentMethod` (String): Payment method used
- `trackingNumber` (String): Shipping tracking number
- `createdAt` (LocalDateTime): When the order was created
- `updatedAt` (LocalDateTime): When the order was last updated

**Entity State**: Uses `meta.state` to track order status (not included in schema)

**Relationships**:
- Many-to-One with User
- Many-to-One with Pet

### 5. User Entity
**Description**: Represents a user/customer of the pet store

**Attributes**:
- `id` (Long): Unique identifier for the user
- `username` (String): Username for login (required, unique)
- `firstName` (String): First name of the user
- `lastName` (String): Last name of the user
- `email` (String): Email address (required, unique)
- `password` (String): Encrypted password (required)
- `phone` (String): Phone number
- `address` (String): Primary address
- `city` (String): City
- `state` (String): State/Province
- `zipCode` (String): ZIP/Postal code
- `country` (String): Country
- `dateOfBirth` (LocalDate): Date of birth
- `preferredPetType` (String): Preferred type of pet
- `isActive` (Boolean): Whether the user account is active
- `emailVerified` (Boolean): Whether email is verified
- `createdAt` (LocalDateTime): When the user account was created
- `updatedAt` (LocalDateTime): When the user account was last updated
- `lastLoginAt` (LocalDateTime): When the user last logged in

**Entity State**: Uses `meta.state` to track user account status (not included in schema)

**Relationships**:
- One-to-Many with Order

## Entity Relationships Summary

```
User (1) -----> (Many) Order
Order (Many) -----> (1) Pet
Pet (Many) -----> (1) Category
Pet (Many) <-----> (Many) Tag
```

## Notes

1. **Entity State Management**: All entities use the internal `meta.state` attribute for workflow state management. This is not part of the entity schema and is managed automatically by the system.

2. **Audit Fields**: All entities include `createdAt` and `updatedAt` timestamps for audit purposes.

3. **Validation**: Required fields are marked as such and should be validated at the API level.

4. **Relationships**: Foreign key relationships are maintained through entity IDs and should be validated during entity operations.

5. **Data Types**: Use appropriate Java data types as specified. BigDecimal for monetary values, LocalDateTime for timestamps, etc.
