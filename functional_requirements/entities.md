# Purrfect Pets API - Entity Requirements

## Overview
The Purrfect Pets API manages a pet store system with pets, customers, orders, and categories. This document defines the entities and their relationships based on the Petstore API data model.

## Entities

### 1. Pet Entity

**Name**: Pet

**Description**: Represents a pet available in the store with all its characteristics and availability status.

**Attributes**:
- `name` (string, required): Name of the pet
- `category_id` (string, optional): Reference to the pet's category
- `photo_urls` (array of strings, required): List of photo URLs for the pet
- `tags` (array of strings, optional): Tags associated with the pet for filtering
- `breed` (string, optional): Specific breed of the pet
- `age` (integer, optional): Age of the pet in months
- `weight` (float, optional): Weight of the pet in kilograms
- `color` (string, optional): Primary color of the pet
- `gender` (string, optional): Gender of the pet (male/female/unknown)
- `vaccination_status` (boolean, optional): Whether the pet is vaccinated
- `microchip_id` (string, optional): Microchip identification number
- `description` (string, optional): Detailed description of the pet
- `price` (float, required): Price of the pet in USD
- `created_at` (string, auto-generated): Timestamp when pet was added
- `updated_at` (string, auto-generated): Timestamp when pet was last updated

**State Management**: 
- Entity state represents the availability status of the pet
- States: available, pending, sold
- Note: The `status` field from Petstore API will be managed as entity.meta.state

**Relationships**:
- Belongs to one Category (many-to-one via category_id)
- Can be in multiple Orders (many-to-many through OrderItem)

### 2. Category Entity

**Name**: Category

**Description**: Represents a category classification for pets (e.g., Dogs, Cats, Birds).

**Attributes**:
- `name` (string, required): Name of the category
- `description` (string, optional): Description of the category
- `icon_url` (string, optional): URL to category icon image
- `display_order` (integer, optional): Order for displaying categories
- `is_featured` (boolean, optional): Whether category is featured on homepage
- `created_at` (string, auto-generated): Timestamp when category was created
- `updated_at` (string, auto-generated): Timestamp when category was last updated

**State Management**:
- Entity state represents the category status
- States: active, inactive
- Categories can be activated/deactivated for display

**Relationships**:
- Has many Pets (one-to-many)

### 3. Customer Entity

**Name**: Customer

**Description**: Represents a customer who can purchase pets from the store.

**Attributes**:
- `username` (string, required): Unique username for the customer
- `first_name` (string, required): Customer's first name
- `last_name` (string, required): Customer's last name
- `email` (string, required): Customer's email address
- `phone` (string, optional): Customer's phone number
- `address` (object, optional): Customer's address with fields:
  - `street` (string): Street address
  - `city` (string): City
  - `state` (string): State/Province
  - `zip_code` (string): ZIP/Postal code
  - `country` (string): Country
- `date_of_birth` (string, optional): Customer's date of birth (ISO date)
- `preferences` (object, optional): Customer preferences:
  - `preferred_pet_types` (array of strings): Preferred pet categories
  - `newsletter_subscription` (boolean): Newsletter subscription status
- `created_at` (string, auto-generated): Timestamp when customer registered
- `updated_at` (string, auto-generated): Timestamp when customer was last updated

**State Management**:
- Entity state represents the customer account status
- States: registered, verified, suspended, deleted
- Customers need email verification after registration

**Relationships**:
- Has many Orders (one-to-many)

### 4. Order Entity

**Name**: Order

**Description**: Represents a purchase order containing one or more pets.

**Attributes**:
- `customer_id` (string, required): Reference to the customer who placed the order
- `order_date` (string, required): Date when the order was placed (ISO datetime)
- `ship_date` (string, optional): Date when the order was shipped (ISO datetime)
- `total_amount` (float, required): Total amount of the order in USD
- `shipping_address` (object, required): Shipping address with same structure as customer address
- `payment_method` (string, required): Payment method used (credit_card, paypal, bank_transfer)
- `payment_reference` (string, optional): Payment transaction reference
- `notes` (string, optional): Special instructions or notes for the order
- `created_at` (string, auto-generated): Timestamp when order was created
- `updated_at` (string, auto-generated): Timestamp when order was last updated

**State Management**:
- Entity state represents the order status
- States: placed, approved, prepared, shipped, delivered, cancelled
- Note: The `status` field from Petstore API will be managed as entity.meta.state

**Relationships**:
- Belongs to one Customer (many-to-one via customer_id)
- Has many OrderItems (one-to-many)

### 5. OrderItem Entity

**Name**: OrderItem

**Description**: Represents individual items (pets) within an order with quantity and pricing details.

**Attributes**:
- `order_id` (string, required): Reference to the parent order
- `pet_id` (string, required): Reference to the pet being ordered
- `quantity` (integer, required): Number of pets ordered (usually 1 for pets)
- `unit_price` (float, required): Price per pet at the time of order
- `subtotal` (float, required): Total price for this line item (quantity * unit_price)
- `special_instructions` (string, optional): Special care instructions for this pet
- `created_at` (string, auto-generated): Timestamp when order item was created

**State Management**:
- Entity state represents the order item status
- States: pending, confirmed, prepared, shipped, delivered
- Individual items can have different states within the same order

**Relationships**:
- Belongs to one Order (many-to-one via order_id)
- References one Pet (many-to-one via pet_id)

## Entity Relationships Summary

```
Category (1) -----> (many) Pet
Customer (1) -----> (many) Order
Order (1) -----> (many) OrderItem
Pet (1) -----> (many) OrderItem
```

## Notes

1. **State vs Status**: All entities use `entity.meta.state` for workflow state management instead of status fields
2. **Timestamps**: All entities have `created_at` and `updated_at` fields managed automatically
3. **IDs**: All entity IDs are strings (UUIDs) as per Cyoda requirements
4. **Pricing**: All monetary values are in USD with float precision
5. **Addresses**: Structured as nested objects for better data organization
6. **Photos**: Pet photos are stored as URL arrays, actual image storage is external
