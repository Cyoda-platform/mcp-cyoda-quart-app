# Processors for Purrfect Pets API

## Pet Processors

### PetRegistrationProcessor

**Entity:** Pet
**Input Data:** Pet entity with basic information (name, category_id, photo_urls, tags, breed, age, weight, color, description, price, vaccination_status)
**What it does:** Validates and registers a new pet in the system
**Expected Output:** Pet entity with generated ID and timestamps, state set to Available

**Pseudocode:**
```
process(pet):
    validate pet.name is not empty and length <= 100
    validate pet.category_id exists in Category table
    validate pet.price >= 0
    validate pet.age >= 0 and age <= 50
    validate pet.weight > 0
    validate photo_urls are valid URLs
    set pet.created_at = current_timestamp
    set pet.updated_at = current_timestamp
    save pet to database
    create inventory record for pet with quantity = 1
    trigger InventoryInitializationProcessor for inventory (null transition)
    return pet
```

### PetReservationProcessor

**Entity:** Pet
**Input Data:** Pet entity, order information
**What it does:** Reserves a pet for an order
**Expected Output:** Pet entity with updated reservation status

**Pseudocode:**
```
process(pet, order_info):
    validate pet is in Available state
    validate order_info contains valid order_id
    update inventory to reserve 1 quantity for pet
    log reservation with order_id and timestamp
    return pet
```

### PetReleaseProcessor

**Entity:** Pet
**Input Data:** Pet entity, order cancellation information
**What it does:** Releases pet reservation when order is cancelled
**Expected Output:** Pet entity released from reservation

**Pseudocode:**
```
process(pet, cancellation_info):
    validate pet is in Pending state
    validate cancellation_info contains order_id
    update inventory to release reserved quantity
    log release with order_id and timestamp
    return pet
```

### PetSaleProcessor

**Entity:** Pet
**Input Data:** Pet entity, completed order information
**What it does:** Marks pet as sold when order is completed
**Expected Output:** Pet entity marked as sold

**Pseudocode:**
```
process(pet, order_info):
    validate pet is in Pending state
    validate order_info contains completed order_id
    update inventory to reduce available quantity by 1
    trigger InventoryUpdateProcessor for inventory (null transition)
    log sale with order_id, sale_date, and price
    return pet
```

## Category Processors

### CategoryActivationProcessor

**Entity:** Category
**Input Data:** Category entity with name and description
**What it does:** Activates a new category
**Expected Output:** Category entity with Active state

**Pseudocode:**
```
process(category):
    validate category.name is not empty and length <= 50
    validate category.name is unique
    set category.created_at = current_timestamp
    set category.updated_at = current_timestamp
    save category to database
    return category
```

### CategoryDeactivationProcessor

**Entity:** Category
**Input Data:** Category entity
**What it does:** Deactivates a category
**Expected Output:** Category entity with Inactive state

**Pseudocode:**
```
process(category):
    validate category is in Active state
    check if any pets are assigned to this category
    if pets exist, return error "Cannot deactivate category with assigned pets"
    set category.updated_at = current_timestamp
    return category
```

### CategoryReactivationProcessor

**Entity:** Category
**Input Data:** Category entity
**What it does:** Reactivates an inactive category
**Expected Output:** Category entity with Active state

**Pseudocode:**
```
process(category):
    validate category is in Inactive state
    set category.updated_at = current_timestamp
    return category
```

## User Processors

### UserRegistrationProcessor

**Entity:** User
**Input Data:** User entity with username, first_name, last_name, email, password, phone, address, user_type
**What it does:** Registers a new user in the system
**Expected Output:** User entity with encrypted password and Active state

**Pseudocode:**
```
process(user):
    validate user.username is unique and length <= 50
    validate user.email is valid format and unique
    validate user.password length >= 8
    validate user.first_name and last_name are not empty
    encrypt user.password using bcrypt
    set user.created_at = current_timestamp
    set user.updated_at = current_timestamp
    if user.user_type is empty, set to "CUSTOMER"
    save user to database
    send welcome email to user.email
    return user
```

### UserSuspensionProcessor

**Entity:** User
**Input Data:** User entity, suspension reason
**What it does:** Suspends a user account
**Expected Output:** User entity with Suspended state

**Pseudocode:**
```
process(user, suspension_info):
    validate user is in Active state
    validate suspension_info contains reason
    log suspension with reason, admin_id, and timestamp
    set user.updated_at = current_timestamp
    send suspension notification email to user.email
    return user
```

### UserDeactivationProcessor

**Entity:** User
**Input Data:** User entity
**What it does:** Deactivates a user account
**Expected Output:** User entity with Inactive state

**Pseudocode:**
```
process(user):
    validate user is in Active state
    cancel all pending orders for user
    trigger OrderCancellationProcessor for each pending order (OrderCancellation transition)
    set user.updated_at = current_timestamp
    send account deactivation email to user.email
    return user
```

### UserReactivationProcessor

**Entity:** User
**Input Data:** User entity, reactivation information
**What it does:** Reactivates a suspended or inactive user
**Expected Output:** User entity with Active state

**Pseudocode:**
```
process(user, reactivation_info):
    validate user is in Suspended or Inactive state
    if user was suspended, validate reactivation_info contains admin approval
    log reactivation with admin_id and timestamp
    set user.updated_at = current_timestamp
    send reactivation confirmation email to user.email
    return user
```
