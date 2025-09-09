# Purrfect Pets API - Entity Requirements

## Overview
The Purrfect Pets API manages a pet store system with pets, orders, users, categories, and tags. This document defines the detailed requirements for each entity, their attributes, and relationships.

## Entities

### 1. Pet Entity

**Name**: Pet  
**Description**: Represents a pet available in the store

**Attributes**:
- `id` (integer): Unique identifier for the pet (auto-generated)
- `name` (string, required): Name of the pet (e.g., "Fluffy", "Buddy")
- `category` (object): Category information containing:
  - `id` (integer): Category identifier
  - `name` (string): Category name (e.g., "Dogs", "Cats", "Birds")
- `photoUrls` (array of strings, required): URLs of pet photos
- `tags` (array of objects): Tags associated with the pet, each containing:
  - `id` (integer): Tag identifier  
  - `name` (string): Tag name (e.g., "friendly", "trained", "vaccinated")
- `description` (string): Detailed description of the pet
- `price` (number): Price of the pet in USD
- `breed` (string): Breed of the pet
- `age` (integer): Age of the pet in months
- `weight` (number): Weight of the pet in kg
- `color` (string): Primary color of the pet
- `gender` (string): Gender of the pet ("male", "female", "unknown")
- `vaccinated` (boolean): Whether the pet is vaccinated
- `neutered` (boolean): Whether the pet is neutered/spayed
- `createdAt` (datetime): When the pet was added to the system
- `updatedAt` (datetime): When the pet was last updated

**Entity State**: The pet's status in the store workflow (not included in schema as it's managed by entity.meta.state)
- States: available, pending, sold

**Relationships**:
- Belongs to one Category
- Has many Tags (many-to-many)
- Can be referenced by many Orders

### 2. Order Entity

**Name**: Order  
**Description**: Represents a purchase order for pets

**Attributes**:
- `id` (integer): Unique identifier for the order (auto-generated)
- `petId` (integer, required): ID of the pet being ordered
- `userId` (integer, required): ID of the user placing the order
- `quantity` (integer, required): Number of pets ordered (default: 1)
- `shipDate` (datetime): Expected shipping date
- `shippingAddress` (object): Shipping address containing:
  - `street` (string): Street address
  - `city` (string): City
  - `state` (string): State/Province
  - `zipCode` (string): ZIP/Postal code
  - `country` (string): Country
- `totalAmount` (number): Total order amount in USD
- `paymentMethod` (string): Payment method used ("credit_card", "paypal", "bank_transfer")
- `paymentStatus` (string): Payment status ("pending", "paid", "failed", "refunded")
- `complete` (boolean): Whether the order is complete
- `notes` (string): Additional order notes
- `createdAt` (datetime): When the order was created
- `updatedAt` (datetime): When the order was last updated

**Entity State**: The order's status in the fulfillment workflow (not included in schema as it's managed by entity.meta.state)
- States: placed, approved, delivered, cancelled

**Relationships**:
- References one Pet
- Belongs to one User

### 3. User Entity

**Name**: User  
**Description**: Represents a user account in the system

**Attributes**:
- `id` (integer): Unique identifier for the user (auto-generated)
- `username` (string, required): Unique username
- `firstName` (string, required): User's first name
- `lastName` (string, required): User's last name
- `email` (string, required): User's email address (unique)
- `password` (string, required): Encrypted password
- `phone` (string): User's phone number
- `address` (object): User's address containing:
  - `street` (string): Street address
  - `city` (string): City
  - `state` (string): State/Province
  - `zipCode` (string): ZIP/Postal code
  - `country` (string): Country
- `dateOfBirth` (date): User's date of birth
- `preferences` (object): User preferences containing:
  - `newsletter` (boolean): Whether to receive newsletters
  - `notifications` (boolean): Whether to receive notifications
  - `preferredCategories` (array of strings): Preferred pet categories
- `createdAt` (datetime): When the user account was created
- `updatedAt` (datetime): When the user account was last updated

**Entity State**: The user's account status (not included in schema as it's managed by entity.meta.state)
- States: active, inactive, suspended, pending_verification

**Relationships**:
- Has many Orders

### 4. Category Entity

**Name**: Category  
**Description**: Represents a pet category for classification

**Attributes**:
- `id` (integer): Unique identifier for the category (auto-generated)
- `name` (string, required): Category name (e.g., "Dogs", "Cats", "Birds", "Fish", "Reptiles")
- `description` (string): Description of the category
- `imageUrl` (string): URL of category image
- `parentCategoryId` (integer): ID of parent category (for subcategories)
- `displayOrder` (integer): Order for displaying categories
- `isActive` (boolean): Whether the category is active
- `createdAt` (datetime): When the category was created
- `updatedAt` (datetime): When the category was last updated

**Entity State**: The category's status (not included in schema as it's managed by entity.meta.state)
- States: active, inactive

**Relationships**:
- Has many Pets
- Can have a parent Category (self-referential)
- Can have many child Categories (self-referential)

### 5. Tag Entity

**Name**: Tag  
**Description**: Represents tags for labeling and filtering pets

**Attributes**:
- `id` (integer): Unique identifier for the tag (auto-generated)
- `name` (string, required): Tag name (e.g., "friendly", "trained", "vaccinated", "hypoallergenic")
- `description` (string): Description of what the tag represents
- `color` (string): Color code for displaying the tag (hex format)
- `category` (string): Tag category ("behavior", "health", "training", "physical")
- `isActive` (boolean): Whether the tag is active
- `createdAt` (datetime): When the tag was created
- `updatedAt` (datetime): When the tag was last updated

**Entity State**: The tag's status (not included in schema as it's managed by entity.meta.state)
- States: active, inactive

**Relationships**:
- Associated with many Pets (many-to-many)

## Entity Relationships Summary

1. **Pet** ↔ **Category**: Many-to-One (Pet belongs to one Category)
2. **Pet** ↔ **Tag**: Many-to-Many (Pet can have multiple Tags, Tag can be on multiple Pets)
3. **Pet** ↔ **Order**: One-to-Many (Pet can be in multiple Orders)
4. **User** ↔ **Order**: One-to-Many (User can have multiple Orders)
5. **Category** ↔ **Category**: Self-referential (Parent-Child relationship)

## Notes

- All entities include `createdAt` and `updatedAt` timestamps for audit purposes
- Entity states are managed by the workflow system and accessed via `entity.meta.state`
- IDs are auto-generated integers for simplicity
- All required fields must be validated before entity creation
- Soft delete should be implemented where appropriate to maintain referential integrity
