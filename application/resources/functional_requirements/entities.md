# Purrfect Pets API - Entity Requirements

## Overview
This document defines the entities for the Purrfect Pets API system, including their attributes and relationships.

## Entities

### 1. Pet Entity

**Description**: Represents a pet available in the store or owned by customers.

**Attributes**:
- `id` (Long): Unique identifier for the pet
- `name` (String): Name of the pet (required)
- `categoryId` (Long): Reference to the category the pet belongs to
- `photoUrls` (List<String>): List of photo URLs for the pet
- `tags` (List<String>): Tags associated with the pet for search and categorization
- `breed` (String): Breed of the pet
- `age` (Integer): Age of the pet in months
- `weight` (Double): Weight of the pet in kilograms
- `color` (String): Primary color of the pet
- `description` (String): Detailed description of the pet
- `price` (Double): Price of the pet
- `vaccinated` (Boolean): Whether the pet is vaccinated
- `neutered` (Boolean): Whether the pet is neutered/spayed
- `microchipped` (Boolean): Whether the pet has a microchip
- `createdAt` (LocalDateTime): When the pet record was created
- `updatedAt` (LocalDateTime): When the pet record was last updated

**Entity State**: The pet's current status in the system workflow (managed by system)
- Note: Do not include 'status' field in schema as it will be managed via entity.meta.state

**Relationships**:
- Many-to-One with Category (via categoryId)
- One-to-Many with OrderItem
- Many-to-One with Owner (when adopted)

### 2. Category Entity

**Description**: Represents categories for organizing pets (e.g., Dogs, Cats, Birds, etc.).

**Attributes**:
- `id` (Long): Unique identifier for the category
- `name` (String): Name of the category (required, unique)
- `description` (String): Description of the category
- `imageUrl` (String): URL for category image
- `createdAt` (LocalDateTime): When the category was created
- `updatedAt` (LocalDateTime): When the category was last updated

**Entity State**: The category's current status in the system workflow (managed by system)

**Relationships**:
- One-to-Many with Pet

### 3. Owner Entity

**Description**: Represents customers who can adopt pets or place orders.

**Attributes**:
- `id` (Long): Unique identifier for the owner
- `firstName` (String): First name of the owner (required)
- `lastName` (String): Last name of the owner (required)
- `email` (String): Email address (required, unique)
- `phone` (String): Phone number
- `address` (String): Home address
- `city` (String): City
- `state` (String): State/Province
- `zipCode` (String): ZIP/Postal code
- `country` (String): Country
- `dateOfBirth` (LocalDate): Date of birth
- `occupation` (String): Occupation
- `housingType` (String): Type of housing (apartment, house, etc.)
- `hasYard` (Boolean): Whether the owner has a yard
- `hasOtherPets` (Boolean): Whether the owner has other pets
- `experienceLevel` (String): Experience level with pets (beginner, intermediate, expert)
- `preferredContactMethod` (String): Preferred contact method (email, phone, text)
- `createdAt` (LocalDateTime): When the owner record was created
- `updatedAt` (LocalDateTime): When the owner record was last updated

**Entity State**: The owner's current status in the system workflow (managed by system)

**Relationships**:
- One-to-Many with Order
- One-to-Many with Pet (adopted pets)
- One-to-Many with AdoptionApplication

### 4. Order Entity

**Description**: Represents orders placed by owners for pets, supplies, or services.

**Attributes**:
- `id` (Long): Unique identifier for the order
- `ownerId` (Long): Reference to the owner placing the order (required)
- `orderDate` (LocalDateTime): When the order was placed
- `shipDate` (LocalDateTime): When the order was shipped
- `totalAmount` (Double): Total amount of the order
- `shippingAddress` (String): Shipping address for the order
- `paymentMethod` (String): Payment method used
- `notes` (String): Additional notes for the order
- `createdAt` (LocalDateTime): When the order was created
- `updatedAt` (LocalDateTime): When the order was last updated

**Entity State**: The order's current status in the system workflow (managed by system)

**Relationships**:
- Many-to-One with Owner (via ownerId)
- One-to-Many with OrderItem

### 5. OrderItem Entity

**Description**: Represents individual items within an order.

**Attributes**:
- `id` (Long): Unique identifier for the order item
- `orderId` (Long): Reference to the parent order (required)
- `petId` (Long): Reference to the pet being ordered (if applicable)
- `productName` (String): Name of the product/service
- `quantity` (Integer): Quantity ordered
- `unitPrice` (Double): Price per unit
- `totalPrice` (Double): Total price for this item (quantity * unitPrice)
- `createdAt` (LocalDateTime): When the order item was created

**Entity State**: The order item's current status in the system workflow (managed by system)

**Relationships**:
- Many-to-One with Order (via orderId)
- Many-to-One with Pet (via petId, optional)

### 6. AdoptionApplication Entity

**Description**: Represents adoption applications submitted by potential owners.

**Attributes**:
- `id` (Long): Unique identifier for the application
- `ownerId` (Long): Reference to the potential owner (required)
- `petId` (Long): Reference to the pet being applied for (required)
- `applicationDate` (LocalDateTime): When the application was submitted
- `reasonForAdoption` (String): Why the owner wants to adopt
- `previousPetExperience` (String): Previous experience with pets
- `livingArrangement` (String): Description of living arrangement
- `workSchedule` (String): Work schedule description
- `veterinarianContact` (String): Contact information for veterinarian
- `references` (List<String>): List of personal references
- `agreedToTerms` (Boolean): Whether applicant agreed to terms and conditions
- `reviewedBy` (String): Staff member who reviewed the application
- `reviewNotes` (String): Notes from the review process
- `createdAt` (LocalDateTime): When the application was created
- `updatedAt` (LocalDateTime): When the application was last updated

**Entity State**: The application's current status in the system workflow (managed by system)

**Relationships**:
- Many-to-One with Owner (via ownerId)
- Many-to-One with Pet (via petId)

## Entity Relationships Summary

```
Owner (1) -----> (M) Order
Owner (1) -----> (M) AdoptionApplication
Owner (1) -----> (M) Pet (adopted pets)

Category (1) -----> (M) Pet

Pet (1) -----> (M) OrderItem
Pet (1) -----> (M) AdoptionApplication

Order (1) -----> (M) OrderItem

AdoptionApplication (M) -----> (1) Owner
AdoptionApplication (M) -----> (1) Pet
```

## Notes

1. All entities use system-managed state via `entity.meta.state` instead of explicit status fields
2. Timestamps (createdAt, updatedAt) are automatically managed by the system
3. All ID fields are auto-generated primary keys
4. Required fields are marked as (required) in the attribute descriptions
5. Unique constraints are noted where applicable (e.g., email for Owner, name for Category)
