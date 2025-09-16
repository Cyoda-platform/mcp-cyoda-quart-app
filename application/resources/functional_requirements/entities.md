# Entities for Purrfect Pets API

## Pet Entity

**Name:** Pet

**Description:** Represents a pet in the Purrfect Pets store with all its characteristics and current availability status.

**Attributes:**
- `id` (Long): Unique identifier for the pet
- `name` (String): Name of the pet (required)
- `category` (Category): Category the pet belongs to
- `photoUrls` (List<String>): List of photo URLs for the pet (required)
- `tags` (List<Tag>): List of tags associated with the pet
- `description` (String): Additional description of the pet
- `price` (BigDecimal): Price of the pet
- `birthDate` (LocalDate): Birth date of the pet
- `breed` (String): Breed of the pet
- `color` (String): Color of the pet
- `weight` (Double): Weight of the pet in kg
- `vaccinated` (Boolean): Whether the pet is vaccinated
- `neutered` (Boolean): Whether the pet is neutered/spayed

**Entity State:** The Pet entity uses `status` semantically as its state, which will be managed by the system as `entity.meta.state`. The possible states are:
- `available`: Pet is available for purchase
- `pending`: Pet is reserved/pending adoption
- `sold`: Pet has been sold/adopted

**Relationships:**
- Many-to-One with Category (Pet belongs to one Category)
- Many-to-Many with Tag (Pet can have multiple Tags)
- One-to-Many with Order (Pet can be in multiple Orders over time)

## Category Entity

**Name:** Category

**Description:** Represents a category of pets (e.g., Dogs, Cats, Birds).

**Attributes:**
- `id` (Long): Unique identifier for the category
- `name` (String): Name of the category (e.g., "Dogs", "Cats")
- `description` (String): Description of the category

**Entity State:** Category is a reference entity and doesn't have workflow states.

**Relationships:**
- One-to-Many with Pet (Category can have multiple Pets)

## Tag Entity

**Name:** Tag

**Description:** Represents tags that can be associated with pets for better categorization and search.

**Attributes:**
- `id` (Long): Unique identifier for the tag
- `name` (String): Name of the tag (e.g., "friendly", "trained", "playful")

**Entity State:** Tag is a reference entity and doesn't have workflow states.

**Relationships:**
- Many-to-Many with Pet (Tag can be associated with multiple Pets)

## Order Entity

**Name:** Order

**Description:** Represents a purchase order for adopting/buying pets.

**Attributes:**
- `id` (Long): Unique identifier for the order
- `petId` (Long): ID of the pet being ordered
- `quantity` (Integer): Quantity of pets (usually 1)
- `shipDate` (LocalDateTime): Expected delivery/pickup date
- `customerName` (String): Name of the customer
- `customerEmail` (String): Email of the customer
- `customerPhone` (String): Phone number of the customer
- `customerAddress` (String): Address of the customer
- `totalAmount` (BigDecimal): Total amount for the order
- `paymentMethod` (String): Payment method used
- `notes` (String): Additional notes for the order

**Entity State:** The Order entity uses `status` semantically as its state, which will be managed by the system as `entity.meta.state`. The possible states are:
- `placed`: Order has been placed
- `approved`: Order has been approved
- `delivered`: Pet has been delivered/picked up

**Relationships:**
- Many-to-One with Pet (Order is for one Pet, but Pet can have multiple Orders)

## User Entity

**Name:** User

**Description:** Represents users of the Purrfect Pets system (customers, staff, admins).

**Attributes:**
- `id` (Long): Unique identifier for the user
- `username` (String): Unique username
- `firstName` (String): First name of the user
- `lastName` (String): Last name of the user
- `email` (String): Email address of the user
- `phone` (String): Phone number of the user
- `role` (String): Role of the user (CUSTOMER, STAFF, ADMIN)
- `registrationDate` (LocalDateTime): Date when user registered
- `lastLoginDate` (LocalDateTime): Last login date

**Entity State:** The User entity uses `userStatus` semantically as its state, which will be managed by the system as `entity.meta.state`. The possible states are:
- `active`: User account is active
- `inactive`: User account is inactive
- `suspended`: User account is suspended

**Relationships:**
- One-to-Many with Order (User can place multiple Orders)
