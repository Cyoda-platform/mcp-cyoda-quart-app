# Processors for Purrfect Pets API

## Pet Processors

### PetRegistrationProcessor
**Entity:** Pet
**Input Data:** Pet entity with basic information (name, category, breed, age, color, weight, description, price, imageUrl)
**What it does:** Validates pet data, assigns unique ID, sets creation timestamp, initializes pet as available
**Expected Output:** Pet entity with state AVAILABLE, populated ID and timestamps

**Pseudocode:**
```
process(pet):
    validate pet.name is not empty
    validate pet.category is valid
    validate pet.price is positive
    validate pet.age is positive
    set pet.id = generateUniqueId()
    set pet.createdAt = currentDateTime()
    set pet.updatedAt = currentDateTime()
    save pet to database
    return pet with state AVAILABLE
```

### PetReservationProcessor
**Entity:** Pet
**Input Data:** Pet entity, owner ID
**What it does:** Reserves pet for specific owner, sets reservation timestamp
**Expected Output:** Pet entity with state PENDING or RESERVED, updated owner reference

**Pseudocode:**
```
process(pet, ownerId):
    validate owner exists and is ACTIVE
    validate pet is AVAILABLE
    set pet.ownerId = ownerId
    set pet.updatedAt = currentDateTime()
    update pet in database
    return pet with state PENDING or RESERVED
```

### PetSaleProcessor
**Entity:** Pet
**Input Data:** Pet entity, order details
**What it does:** Completes pet sale, creates order record, updates pet status
**Expected Output:** Pet entity with state SOLD, Order entity created with state PLACED

**Pseudocode:**
```
process(pet, orderDetails):
    validate pet is PENDING
    validate owner is ACTIVE
    create new order with pet and owner details
    set order.totalAmount = pet.price
    set order.orderDate = currentDateTime()
    save order to database
    set pet.updatedAt = currentDateTime()
    update pet in database
    trigger order workflow transition to PLACED
    return pet with state SOLD
```

### PetReservationCancelProcessor
**Entity:** Pet
**Input Data:** Pet entity
**What it does:** Cancels pet reservation, makes pet available again
**Expected Output:** Pet entity with state AVAILABLE, owner reference cleared

**Pseudocode:**
```
process(pet):
    validate pet is PENDING or RESERVED
    set pet.ownerId = null
    set pet.updatedAt = currentDateTime()
    update pet in database
    return pet with state AVAILABLE
```

### PetArchiveProcessor
**Entity:** Pet
**Input Data:** Pet entity
**What it does:** Archives sold pet, marks as unavailable
**Expected Output:** Pet entity with state UNAVAILABLE

**Pseudocode:**
```
process(pet):
    validate pet is SOLD
    set pet.updatedAt = currentDateTime()
    update pet in database
    return pet with state UNAVAILABLE
```

## Owner Processors

### OwnerRegistrationProcessor
**Entity:** Owner
**Input Data:** Owner entity with personal information
**What it does:** Validates owner data, creates account, sends verification email
**Expected Output:** Owner entity with state PENDING_VERIFICATION

**Pseudocode:**
```
process(owner):
    validate owner.email is unique and valid format
    validate owner.firstName and lastName are not empty
    validate owner.phone is valid format
    set owner.id = generateUniqueId()
    set owner.createdAt = currentDateTime()
    set owner.updatedAt = currentDateTime()
    save owner to database
    send verification email to owner.email
    return owner with state PENDING_VERIFICATION
```

### OwnerVerificationProcessor
**Entity:** Owner
**Input Data:** Owner entity, verification token
**What it does:** Verifies owner email, activates account
**Expected Output:** Owner entity with state ACTIVE

**Pseudocode:**
```
process(owner, verificationToken):
    validate verification token is valid and not expired
    validate owner is PENDING_VERIFICATION
    set owner.updatedAt = currentDateTime()
    update owner in database
    send welcome email to owner
    return owner with state ACTIVE
```

### OwnerDeactivationProcessor
**Entity:** Owner
**Input Data:** Owner entity, reason
**What it does:** Deactivates owner account, cancels active reservations
**Expected Output:** Owner entity with state INACTIVE

**Pseudocode:**
```
process(owner, reason):
    validate owner is ACTIVE
    cancel all PENDING pet reservations for owner
    set owner.updatedAt = currentDateTime()
    update owner in database
    log deactivation reason
    return owner with state INACTIVE
```

### OwnerActivationProcessor
**Entity:** Owner
**Input Data:** Owner entity
**What it does:** Reactivates owner account
**Expected Output:** Owner entity with state ACTIVE

**Pseudocode:**
```
process(owner):
    validate owner is INACTIVE
    validate owner account is in good standing
    set owner.updatedAt = currentDateTime()
    update owner in database
    send reactivation email to owner
    return owner with state ACTIVE
```

### OwnerSuspensionProcessor
**Entity:** Owner
**Input Data:** Owner entity, suspension reason
**What it does:** Suspends owner account, cancels reservations
**Expected Output:** Owner entity with state SUSPENDED

**Pseudocode:**
```
process(owner, suspensionReason):
    validate owner is ACTIVE
    cancel all PENDING pet reservations for owner
    set owner.updatedAt = currentDateTime()
    update owner in database
    log suspension reason
    send suspension notification email
    return owner with state SUSPENDED
```

### OwnerReinstateProcessor
**Entity:** Owner
**Input Data:** Owner entity
**What it does:** Reinstates suspended owner account
**Expected Output:** Owner entity with state ACTIVE

**Pseudocode:**
```
process(owner):
    validate owner is SUSPENDED
    validate suspension period is complete
    set owner.updatedAt = currentDateTime()
    update owner in database
    send reinstatement email to owner
    return owner with state ACTIVE
```

## Order Processors

### OrderCreationProcessor
**Entity:** Order
**Input Data:** Order entity with pet ID, owner ID, delivery details
**What it does:** Creates new order, validates pet availability, calculates total
**Expected Output:** Order entity with state PLACED

**Pseudocode:**
```
process(order):
    validate pet exists and is AVAILABLE
    validate owner exists and is ACTIVE
    validate delivery address is provided
    set order.id = generateUniqueId()
    set order.totalAmount = pet.price * order.quantity
    set order.orderDate = currentDateTime()
    set order.createdAt = currentDateTime()
    set order.updatedAt = currentDateTime()
    save order to database
    trigger pet workflow transition to PENDING
    return order with state PLACED
```

### OrderConfirmationProcessor
**Entity:** Order
**Input Data:** Order entity
**What it does:** Confirms order, validates payment, reserves pet
**Expected Output:** Order entity with state CONFIRMED

**Pseudocode:**
```
process(order):
    validate order is PLACED
    validate payment information is valid
    validate pet is still available
    process payment
    set order.updatedAt = currentDateTime()
    update order in database
    send confirmation email to owner
    return order with state CONFIRMED
```

### OrderPreparationProcessor
**Entity:** Order
**Input Data:** Order entity
**What it does:** Begins order preparation, schedules delivery
**Expected Output:** Order entity with state PREPARING

**Pseudocode:**
```
process(order):
    validate order is CONFIRMED
    schedule delivery date
    prepare pet documentation
    set order.updatedAt = currentDateTime()
    update order in database
    send preparation notification to owner
    return order with state PREPARING
```

### OrderShippingProcessor
**Entity:** Order
**Input Data:** Order entity, tracking information
**What it does:** Ships order, provides tracking details
**Expected Output:** Order entity with state SHIPPED

**Pseudocode:**
```
process(order, trackingInfo):
    validate order is PREPARING
    validate pet is ready for delivery
    create shipping label
    set order.updatedAt = currentDateTime()
    update order in database
    send shipping notification with tracking to owner
    return order with state SHIPPED
```

### OrderDeliveryProcessor
**Entity:** Order
**Input Data:** Order entity, delivery confirmation
**What it does:** Confirms delivery, completes order
**Expected Output:** Order entity with state DELIVERED

**Pseudocode:**
```
process(order, deliveryConfirmation):
    validate order is SHIPPED
    validate delivery confirmation
    set order.updatedAt = currentDateTime()
    update order in database
    trigger pet workflow transition to SOLD
    send delivery confirmation to owner
    return order with state DELIVERED
```

### OrderCancellationProcessor
**Entity:** Order
**Input Data:** Order entity, cancellation reason
**What it does:** Cancels order, refunds payment, releases pet
**Expected Output:** Order entity with state CANCELLED

**Pseudocode:**
```
process(order, cancellationReason):
    validate order is PLACED or CONFIRMED
    process refund if payment was made
    trigger pet workflow transition to AVAILABLE (null transition)
    set order.updatedAt = currentDateTime()
    update order in database
    log cancellation reason
    send cancellation notification to owner
    return order with state CANCELLED
```

### OrderReturnProcessor
**Entity:** Order
**Input Data:** Order entity, return reason
**What it does:** Processes order return, handles refund
**Expected Output:** Order entity with state RETURNED

**Pseudocode:**
```
process(order, returnReason):
    validate order is DELIVERED
    validate return is within return period
    process refund
    trigger pet workflow transition to AVAILABLE (null transition)
    set order.updatedAt = currentDateTime()
    update order in database
    log return reason
    send return confirmation to owner
    return order with state RETURNED
```

## Category Processors

### CategoryCreationProcessor
**Entity:** Category
**Input Data:** Category entity with name, description
**What it does:** Creates new category, validates uniqueness
**Expected Output:** Category entity with state ACTIVE

**Pseudocode:**
```
process(category):
    validate category.name is unique and not empty
    validate category.description is provided
    set category.id = generateUniqueId()
    set category.isActive = true
    set category.createdAt = currentDateTime()
    set category.updatedAt = currentDateTime()
    save category to database
    return category with state ACTIVE
```

### CategoryDeactivationProcessor
**Entity:** Category
**Input Data:** Category entity
**What it does:** Deactivates category, handles associated pets
**Expected Output:** Category entity with state INACTIVE

**Pseudocode:**
```
process(category):
    validate category is ACTIVE
    check if category has active pets
    set category.isActive = false
    set category.updatedAt = currentDateTime()
    update category in database
    return category with state INACTIVE
```

### CategoryActivationProcessor
**Entity:** Category
**Input Data:** Category entity
**What it does:** Reactivates category
**Expected Output:** Category entity with state ACTIVE

**Pseudocode:**
```
process(category):
    validate category is INACTIVE
    set category.isActive = true
    set category.updatedAt = currentDateTime()
    update category in database
    return category with state ACTIVE
```

### CategoryArchiveProcessor
**Entity:** Category
**Input Data:** Category entity
**What it does:** Archives category permanently
**Expected Output:** Category entity with state ARCHIVED

**Pseudocode:**
```
process(category):
    validate category is INACTIVE
    validate no active pets in category
    set category.updatedAt = currentDateTime()
    update category in database
    return category with state ARCHIVED
```
