# Entities for Purrfect Pets API

## Pet Entity

**Name:** Pet

**Attributes:**
- id: Long (Primary Key)
- name: String (required)
- category_id: Long (Foreign Key to Category)
- photo_urls: List<String>
- tags: List<String>
- breed: String
- age: Integer
- weight: Double
- color: String
- description: String
- price: Double
- created_at: LocalDateTime
- updated_at: LocalDateTime

**Relationships:**
- Many-to-One with Category (category_id -> Category.id)
- One-to-Many with OrderItem (Pet.id -> OrderItem.pet_id)

**State Management:**
- Entity state is managed internally via entity.meta.state
- States: DRAFT, AVAILABLE, PENDING, SOLD, UNAVAILABLE

## Category Entity

**Name:** Category

**Attributes:**
- id: Long (Primary Key)
- name: String (required, unique)
- description: String
- created_at: LocalDateTime
- updated_at: LocalDateTime

**Relationships:**
- One-to-Many with Pet (Category.id -> Pet.category_id)

**State Management:**
- Entity state is managed internally via entity.meta.state
- States: DRAFT, ACTIVE, INACTIVE

## Customer Entity

**Name:** Customer

**Attributes:**
- id: Long (Primary Key)
- username: String (required, unique)
- first_name: String (required)
- last_name: String (required)
- email: String (required, unique)
- phone: String
- address: String
- city: String
- state: String
- zip_code: String
- country: String
- created_at: LocalDateTime
- updated_at: LocalDateTime

**Relationships:**
- One-to-Many with Order (Customer.id -> Order.customer_id)

**State Management:**
- Entity state is managed internally via entity.meta.state
- States: PENDING_VERIFICATION, ACTIVE, SUSPENDED, INACTIVE

## Order Entity

**Name:** Order

**Attributes:**
- id: Long (Primary Key)
- customer_id: Long (Foreign Key to Customer)
- order_date: LocalDateTime
- ship_date: LocalDateTime
- total_amount: Double
- shipping_address: String
- shipping_city: String
- shipping_state: String
- shipping_zip: String
- shipping_country: String
- created_at: LocalDateTime
- updated_at: LocalDateTime

**Relationships:**
- Many-to-One with Customer (order.customer_id -> Customer.id)
- One-to-Many with OrderItem (Order.id -> OrderItem.order_id)

**State Management:**
- Entity state is managed internally via entity.meta.state
- States: DRAFT, PLACED, APPROVED, SHIPPED, DELIVERED, CANCELLED

## OrderItem Entity

**Name:** OrderItem

**Attributes:**
- id: Long (Primary Key)
- order_id: Long (Foreign Key to Order)
- pet_id: Long (Foreign Key to Pet)
- quantity: Integer (required)
- unit_price: Double (required)
- total_price: Double (calculated)
- created_at: LocalDateTime
- updated_at: LocalDateTime

**Relationships:**
- Many-to-One with Order (order_item.order_id -> Order.id)
- Many-to-One with Pet (order_item.pet_id -> Pet.id)

**State Management:**
- Entity state is managed internally via entity.meta.state
- States: DRAFT, CONFIRMED, CANCELLED

## Notes

1. All entities use entity.meta.state for state management - do not include state/status fields in the schema
2. All timestamps are automatically managed by the system
3. Foreign key relationships ensure data integrity
4. Price calculations are handled by processors during transitions
5. The system will automatically manage state transitions based on the defined workflows
