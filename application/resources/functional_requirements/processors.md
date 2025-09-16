# Processors for Purrfect Pets API

## Pet Processors

### PetRegistrationProcessor

**Entity:** Pet
**Input Data:** Pet entity with basic information (name, category, photoUrls, etc.)
**Description:** Validates and registers a new pet in the system
**Output:** Pet entity with assigned ID and status set to 'available'
**Transition:** None (automatic transition to available state)

**Pseudocode:**
```
process(pet):
    validate pet.name is not empty
    validate pet.photoUrls is not empty
    validate pet.category exists
    if pet.price is null:
        set pet.price to default value based on category
    if pet.description is empty:
        generate default description based on name and category
    assign unique ID to pet
    set pet creation timestamp
    save pet to database
    return pet
```

### PetReservationProcessor

**Entity:** Pet
**Input Data:** Pet entity and customer information
**Description:** Reserves a pet for a potential customer
**Output:** Pet entity with reservation details
**Transition:** available → pending

**Pseudocode:**
```
process(pet, customerInfo):
    validate customer information is complete
    create reservation record with expiration time (24 hours)
    set pet.reservedBy = customerInfo.customerId
    set pet.reservationExpiry = current time + 24 hours
    send reservation confirmation email to customer
    return pet
```

### PetReservationCancellationProcessor

**Entity:** Pet
**Input Data:** Pet entity
**Description:** Cancels pet reservation and makes it available again
**Output:** Pet entity with cleared reservation
**Transition:** pending → available

**Pseudocode:**
```
process(pet):
    clear pet.reservedBy
    clear pet.reservationExpiry
    delete reservation record
    send cancellation notification if customer exists
    return pet
```

### PetSaleProcessor

**Entity:** Pet
**Input Data:** Pet entity and order information
**Description:** Completes the sale of a reserved pet
**Output:** Pet entity marked as sold, Order entity created
**Transition:** pending → sold

**Pseudocode:**
```
process(pet, orderInfo):
    validate order information is complete
    validate payment information
    create order record with status 'placed'
    clear pet reservation details
    set pet.soldDate = current date
    set pet.soldTo = orderInfo.customerId
    trigger OrderCreationProcessor for new order
    send sale confirmation to customer
    return pet
```

### PetDirectSaleProcessor

**Entity:** Pet
**Input Data:** Pet entity and order information
**Description:** Directly sells an available pet without reservation
**Output:** Pet entity marked as sold, Order entity created
**Transition:** available → sold

**Pseudocode:**
```
process(pet, orderInfo):
    validate order information is complete
    validate payment information
    create order record with status 'placed'
    set pet.soldDate = current date
    set pet.soldTo = orderInfo.customerId
    trigger OrderCreationProcessor for new order
    send sale confirmation to customer
    return pet
```

## Order Processors

### OrderCreationProcessor

**Entity:** Order
**Input Data:** Order entity with customer and pet information
**Description:** Creates and validates a new order
**Output:** Order entity with assigned ID and status 'placed'
**Transition:** None (automatic transition to placed state)

**Pseudocode:**
```
process(order):
    validate order.petId exists and is available/pending
    validate customer information is complete
    calculate total amount based on pet price and quantity
    assign unique order ID
    set order.orderDate = current date
    set order.estimatedDelivery = current date + 3 days
    save order to database
    send order confirmation email
    return order
```

### OrderApprovalProcessor

**Entity:** Order
**Input Data:** Order entity
**Description:** Approves an order after validation
**Output:** Order entity with status 'approved'
**Transition:** placed → approved

**Pseudocode:**
```
process(order):
    validate payment is confirmed
    validate pet is still available
    validate customer details
    set order.approvedDate = current date
    set order.approvedBy = current user
    send approval notification to customer
    schedule delivery/pickup
    return order
```

### OrderUpdateProcessor

**Entity:** Order
**Input Data:** Order entity with updated information
**Description:** Updates order details while in placed state
**Output:** Updated order entity
**Transition:** placed → placed (loop)

**Pseudocode:**
```
process(order, updates):
    validate order is in 'placed' state
    validate updates are allowed (customer info, delivery address, etc.)
    apply updates to order
    recalculate total if necessary
    set order.lastModified = current date
    send update notification to customer
    return order
```

### OrderDeliveryProcessor

**Entity:** Order
**Input Data:** Order entity and delivery confirmation
**Description:** Marks order as delivered when pet is handed over
**Output:** Order entity with status 'delivered'
**Transition:** approved → delivered

**Pseudocode:**
```
process(order, deliveryInfo):
    validate order is in 'approved' state
    validate delivery information
    set order.deliveredDate = current date
    set order.deliveredBy = deliveryInfo.staffMember
    set order.deliverySignature = deliveryInfo.signature
    send delivery confirmation to customer
    trigger post-delivery follow-up email (scheduled)
    return order
```

## User Processors

### UserRegistrationProcessor

**Entity:** User
**Input Data:** User entity with registration information
**Description:** Registers a new user in the system
**Output:** User entity with assigned ID and status 'active'
**Transition:** None (automatic transition to active state)

**Pseudocode:**
```
process(user):
    validate username is unique
    validate email is unique and valid format
    validate password meets security requirements
    hash password
    assign unique user ID
    set user.registrationDate = current date
    set user.role = 'CUSTOMER' (default)
    save user to database
    send welcome email
    return user
```

### UserDeactivationProcessor

**Entity:** User
**Input Data:** User entity
**Description:** Deactivates a user account
**Output:** User entity with status 'inactive'
**Transition:** active → inactive

**Pseudocode:**
```
process(user):
    set user.deactivatedDate = current date
    set user.deactivatedBy = current admin user
    cancel any active sessions
    send deactivation notification
    return user
```

### UserReactivationProcessor

**Entity:** User
**Input Data:** User entity
**Description:** Reactivates an inactive user account
**Output:** User entity with status 'active'
**Transition:** inactive → active

**Pseudocode:**
```
process(user):
    validate reactivation is allowed
    clear user.deactivatedDate
    set user.reactivatedDate = current date
    send reactivation confirmation email
    return user
```

### UserSuspensionProcessor

**Entity:** User
**Input Data:** User entity and suspension reason
**Description:** Suspends a user account for violations
**Output:** User entity with status 'suspended'
**Transition:** active → suspended

**Pseudocode:**
```
process(user, suspensionInfo):
    validate suspension reason is provided
    set user.suspendedDate = current date
    set user.suspendedBy = current admin user
    set user.suspensionReason = suspensionInfo.reason
    set user.suspensionExpiry = suspensionInfo.expiryDate
    cancel any active sessions
    send suspension notification
    return user
```

### UserUnsuspensionProcessor

**Entity:** User
**Input Data:** User entity
**Description:** Removes suspension and reactivates account
**Output:** User entity with status 'active'
**Transition:** suspended → active

**Pseudocode:**
```
process(user):
    validate unsuspension is allowed
    clear user.suspendedDate
    clear user.suspensionReason
    clear user.suspensionExpiry
    set user.unsuspendedDate = current date
    send unsuspension confirmation email
    return user
```
