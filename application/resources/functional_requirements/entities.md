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
- created_at: LocalDateTime (Auto-generated)
- updated_at: LocalDateTime (Auto-updated)

**Relationships:**
- Many-to-One with Category (category_id)
- One-to-Many with OrderItem (pet_id)

**Entity State:** Available, Pending, Sold

---

## Category Entity

**Name:** Category

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- name: String (Required, unique, max 50 characters)
- description: String (Category description, max 200 characters)
- created_at: LocalDateTime (Auto-generated)
- updated_at: LocalDateTime (Auto-updated)

**Relationships:**
- One-to-Many with Pet (category_id)

**Entity State:** Active, Inactive

---

## User Entity

**Name:** User

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- username: String (Required, unique, max 50 characters)
- first_name: String (Required, max 50 characters)
- last_name: String (Required, max 50 characters)
- email: String (Required, unique, valid email format)
- password: String (Required, encrypted, min 8 characters)
- phone: String (Phone number, max 20 characters)
- address: String (User address, max 200 characters)
- user_type: String (CUSTOMER, ADMIN, STAFF)
- created_at: LocalDateTime (Auto-generated)
- updated_at: LocalDateTime (Auto-updated)

**Relationships:**
- One-to-Many with Order (user_id)

**Entity State:** Active, Inactive, Suspended

---

## Order Entity

**Name:** Order

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- user_id: Long (Foreign Key to User)
- order_date: LocalDateTime (Auto-generated)
- ship_date: LocalDateTime (Shipping date)
- total_amount: Double (Total order amount)
- shipping_address: String (Shipping address, max 300 characters)
- payment_method: String (CREDIT_CARD, DEBIT_CARD, CASH, BANK_TRANSFER)
- notes: String (Order notes, max 500 characters)
- created_at: LocalDateTime (Auto-generated)
- updated_at: LocalDateTime (Auto-updated)

**Relationships:**
- Many-to-One with User (user_id)
- One-to-Many with OrderItem (order_id)

**Entity State:** Placed, Approved, Preparing, Shipped, Delivered, Cancelled

---

## OrderItem Entity

**Name:** OrderItem

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- order_id: Long (Foreign Key to Order)
- pet_id: Long (Foreign Key to Pet)
- quantity: Integer (Required, min 1)
- unit_price: Double (Price per unit)
- total_price: Double (quantity * unit_price)
- created_at: LocalDateTime (Auto-generated)
- updated_at: LocalDateTime (Auto-updated)

**Relationships:**
- Many-to-One with Order (order_id)
- Many-to-One with Pet (pet_id)

**Entity State:** Added, Confirmed, Cancelled

---

## Inventory Entity

**Name:** Inventory

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- pet_id: Long (Foreign Key to Pet, unique)
- quantity: Integer (Available quantity, min 0)
- reserved_quantity: Integer (Reserved for pending orders, min 0)
- reorder_level: Integer (Minimum stock level, min 0)
- last_restocked: LocalDateTime (Last restock date)
- created_at: LocalDateTime (Auto-generated)
- updated_at: LocalDateTime (Auto-updated)

**Relationships:**
- One-to-One with Pet (pet_id)

**Entity State:** InStock, LowStock, OutOfStock, Discontinued

---

## Review Entity

**Name:** Review

**Attributes:**
- id: Long (Primary Key, Auto-generated)
- pet_id: Long (Foreign Key to Pet)
- user_id: Long (Foreign Key to User)
- rating: Integer (Rating from 1 to 5)
- comment: String (Review comment, max 1000 characters)
- helpful_count: Integer (Number of helpful votes, default 0)
- created_at: LocalDateTime (Auto-generated)
- updated_at: LocalDateTime (Auto-updated)

**Relationships:**
- Many-to-One with Pet (pet_id)
- Many-to-One with User (user_id)

**Entity State:** Pending, Approved, Rejected

---

## Notes on Entity States

- Entity states are managed automatically by the workflow system
- States are accessed via `entity.meta.state` in processor code
- States cannot be directly modified by processors
- State transitions are controlled by workflow definitions
- If user requirements mention status/state fields, they are replaced by the internal state system
