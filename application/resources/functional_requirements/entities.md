# Entities for Purrfect Pets API

## Pet Entity

**Name:** Pet

**Attributes:**
- id: Long (unique identifier)
- name: String (pet's name)
- category: String (e.g., "Dog", "Cat", "Bird", "Fish")
- breed: String (specific breed)
- age: Integer (age in years)
- color: String (primary color)
- weight: Double (weight in kg)
- description: String (detailed description)
- price: Double (price in USD)
- imageUrl: String (URL to pet's photo)
- ownerId: Long (reference to owner, nullable)
- createdAt: LocalDateTime
- updatedAt: LocalDateTime

**Relationships:**
- Many-to-One with Owner (a pet can have one owner, an owner can have multiple pets)
- One-to-Many with Order (a pet can be in multiple orders over time)

**State Management:**
- Entity state managed by system via entity.meta.state
- States: AVAILABLE, PENDING, SOLD, RESERVED, UNAVAILABLE

## Owner Entity

**Name:** Owner

**Attributes:**
- id: Long (unique identifier)
- firstName: String
- lastName: String
- email: String (unique)
- phone: String
- address: String
- city: String
- zipCode: String
- country: String
- dateOfBirth: LocalDate
- createdAt: LocalDateTime
- updatedAt: LocalDateTime

**Relationships:**
- One-to-Many with Pet (an owner can have multiple pets)
- One-to-Many with Order (an owner can place multiple orders)

**State Management:**
- Entity state managed by system via entity.meta.state
- States: ACTIVE, INACTIVE, SUSPENDED, PENDING_VERIFICATION

## Order Entity

**Name:** Order

**Attributes:**
- id: Long (unique identifier)
- ownerId: Long (reference to owner)
- petId: Long (reference to pet)
- quantity: Integer (typically 1 for pets)
- totalAmount: Double (total order amount)
- orderDate: LocalDateTime
- deliveryDate: LocalDate (expected delivery)
- deliveryAddress: String
- notes: String (special instructions)
- createdAt: LocalDateTime
- updatedAt: LocalDateTime

**Relationships:**
- Many-to-One with Owner (an order belongs to one owner)
- Many-to-One with Pet (an order is for one pet)

**State Management:**
- Entity state managed by system via entity.meta.state
- States: PLACED, CONFIRMED, PREPARING, SHIPPED, DELIVERED, CANCELLED, RETURNED

## Category Entity

**Name:** Category

**Attributes:**
- id: Long (unique identifier)
- name: String (category name like "Dogs", "Cats", etc.)
- description: String (category description)
- imageUrl: String (category image)
- isActive: Boolean (whether category is active)
- createdAt: LocalDateTime
- updatedAt: LocalDateTime

**Relationships:**
- One-to-Many with Pet (a category can have multiple pets)

**State Management:**
- Entity state managed by system via entity.meta.state
- States: ACTIVE, INACTIVE, ARCHIVED
