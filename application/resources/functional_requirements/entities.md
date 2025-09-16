# Entities for Purrfect Pets API

## Pet Entity

**Name:** Pet

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- name: String (Required, max 100 characters)
- category_id: Long (Foreign Key to Category)
- photo_urls: List<String> (URLs to pet photos)
- tags: List<String> (Pet tags for categorization)
- breed: String (Pet breed, max 50 characters)
- age: Integer (Pet age in years)
- weight: Double (Pet weight in kg)
- color: String (Pet color, max 30 characters)
- description: String (Pet description, max 500 characters)
- price: Double (Pet price)
- vaccination_status: Boolean (Whether pet is vaccinated)
- created_at: DateTime (Auto-generated)
- updated_at: DateTime (Auto-updated)

**Relationships:**
- Many-to-One with Category (category_id)
- One-to-Many with OrderItem (pet_id)

**Note:** Pet state represents the availability status (available, pending, sold) and is managed by the system via entity.meta.state.

## Category Entity

**Name:** Category

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- name: String (Required, unique, max 50 characters)
- description: String (Category description, max 200 characters)
- created_at: DateTime (Auto-generated)
- updated_at: DateTime (Auto-updated)

**Relationships:**
- One-to-Many with Pet (category_id)

**Note:** Category state represents the category status (active, inactive) and is managed by the system via entity.meta.state.

## User Entity

**Name:** User

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- username: String (Required, unique, max 50 characters)
- first_name: String (Required, max 50 characters)
- last_name: String (Required, max 50 characters)
- email: String (Required, unique, valid email format)
- password: String (Required, hashed, min 8 characters)
- phone: String (Phone number, max 20 characters)
- address: String (User address, max 200 characters)
- user_type: String (customer, admin, staff)
- created_at: DateTime (Auto-generated)
- updated_at: DateTime (Auto-updated)

**Relationships:**
- One-to-Many with Order (user_id)

**Note:** User state represents the account status (active, inactive, suspended) and is managed by the system via entity.meta.state.

## Order Entity

**Name:** Order

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- user_id: Long (Foreign Key to User)
- order_date: DateTime (Auto-generated)
- ship_date: DateTime (Estimated shipping date)
- total_amount: Double (Total order amount)
- shipping_address: String (Shipping address, max 300 characters)
- payment_method: String (Payment method used)
- notes: String (Order notes, max 500 characters)
- created_at: DateTime (Auto-generated)
- updated_at: DateTime (Auto-updated)

**Relationships:**
- Many-to-One with User (user_id)
- One-to-Many with OrderItem (order_id)

**Note:** Order state represents the order status (placed, approved, delivered, cancelled) and is managed by the system via entity.meta.state.

## OrderItem Entity

**Name:** OrderItem

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- order_id: Long (Foreign Key to Order)
- pet_id: Long (Foreign Key to Pet)
- quantity: Integer (Quantity of pets ordered, default 1)
- unit_price: Double (Price per pet at time of order)
- total_price: Double (quantity * unit_price)
- created_at: DateTime (Auto-generated)
- updated_at: DateTime (Auto-updated)

**Relationships:**
- Many-to-One with Order (order_id)
- Many-to-One with Pet (pet_id)

**Note:** OrderItem state represents the item status (pending, confirmed, shipped) and is managed by the system via entity.meta.state.
