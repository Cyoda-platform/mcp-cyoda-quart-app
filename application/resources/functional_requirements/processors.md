# Processors Specification for Purrfect Pets API

## Overview
This document defines the processors for handling business logic during workflow transitions.

## Pet Processors

### PetValidationProcessor
**Entity**: Pet  
**Input**: Pet entity with basic information  
**Purpose**: Validates pet data and sets up initial state  
**Output**: Pet entity with validated data and AVAILABLE state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(pet):
    validate pet.name is not empty
    validate pet.photoUrls is not empty
    validate pet.category exists
    validate pet.price is positive
    if pet.birthDate exists:
        validate birthDate is not in future
    set default values for missing optional fields
    return pet
```

### PetReservationProcessor
**Entity**: Pet  
**Input**: Pet entity and reservation details  
**Purpose**: Reserves pet for customer or order  
**Output**: Pet entity with PENDING or RESERVED state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(pet, reservationData):
    validate pet is in AVAILABLE state
    if reservationData.orderId exists:
        create reservation record with orderId
        log reservation activity
    else:
        create customer reservation with customerId
        set reservation expiry time (24 hours)
    return pet
```

### PetSaleProcessor
**Entity**: Pet  
**Input**: Pet entity and sale information  
**Purpose**: Completes pet sale transaction  
**Output**: Pet entity with SOLD state, updates related order item  
**Transition**: OrderItem to DELIVERED state

**Pseudocode**:
```
process(pet, saleData):
    validate pet is in PENDING state
    validate associated order exists
    update order item status to DELIVERED
    record sale transaction
    update pet availability
    send notification to customer
    return pet
```

### PetReleaseProcessor
**Entity**: Pet  
**Input**: Pet entity  
**Purpose**: Releases pet reservation and returns to available  
**Output**: Pet entity with AVAILABLE state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(pet):
    remove any existing reservations
    clear pending order associations
    log release activity
    return pet to available inventory
    return pet
```

## Category Processors

### CategoryValidationProcessor
**Entity**: Category  
**Input**: Category entity  
**Purpose**: Validates category data  
**Output**: Category entity with ACTIVE state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(category):
    validate category.name is not empty
    validate category.name is unique
    set default description if empty
    return category
```

## Tag Processors

### TagValidationProcessor
**Entity**: Tag  
**Input**: Tag entity  
**Purpose**: Validates tag data  
**Output**: Tag entity with ACTIVE state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(tag):
    validate tag.name is not empty
    validate tag.name is unique
    set default color if empty
    return tag
```

## User Processors

### UserRegistrationProcessor
**Entity**: User  
**Input**: User entity with registration data  
**Purpose**: Processes user registration  
**Output**: User entity with PENDING_VERIFICATION state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(user):
    validate user.email is valid format
    validate user.email is unique
    validate user.username is unique
    encrypt user.password
    set user.registrationDate to current time
    generate email verification token
    send verification email
    return user
```

### UserVerificationProcessor
**Entity**: User  
**Input**: User entity and verification token  
**Purpose**: Verifies user email and activates account  
**Output**: User entity with ACTIVE state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(user, verificationToken):
    validate verification token
    check token expiry
    mark email as verified
    set account activation date
    send welcome email
    return user
```

### UserSuspensionProcessor
**Entity**: User  
**Input**: User entity and suspension reason  
**Purpose**: Suspends user account  
**Output**: User entity with SUSPENDED state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(user, suspensionReason):
    record suspension reason
    set suspension date
    cancel active sessions
    send suspension notification
    return user
```

### UserActivationProcessor
**Entity**: User  
**Input**: User entity  
**Purpose**: Activates or reactivates user account  
**Output**: User entity with ACTIVE state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(user):
    clear suspension flags
    set reactivation date
    send reactivation notification
    return user
```

## Order Processors

### OrderCreationProcessor
**Entity**: Order  
**Input**: Order entity with order items  
**Purpose**: Creates and validates new order  
**Output**: Order entity with PLACED state, creates order items  
**Transition**: OrderItem entities to PENDING state

**Pseudocode**:
```
process(order):
    validate user exists and is active
    validate order has at least one item
    for each order item:
        validate pet exists and is available
        calculate item total price
        create order item entity
        reserve pet (trigger Pet to PENDING)
    calculate order total amount
    set order.orderDate to current time
    return order
```

### OrderApprovalProcessor
**Entity**: Order  
**Input**: Order entity  
**Purpose**: Approves order for processing  
**Output**: Order entity with APPROVED state  
**Transition**: OrderItem entities to CONFIRMED state

**Pseudocode**:
```
process(order):
    validate payment information
    validate inventory availability
    for each order item:
        confirm item availability
        update item to CONFIRMED state
    send order confirmation email
    return order
```

### OrderDeliveryProcessor
**Entity**: Order  
**Input**: Order entity and delivery information  
**Purpose**: Marks order as delivered  
**Output**: Order entity with DELIVERED state  
**Transition**: Pet entities to SOLD state, OrderItem entities to DELIVERED state

**Pseudocode**:
```
process(order, deliveryInfo):
    validate all items are ready for delivery
    set order.shipDate to current time
    for each order item:
        mark item as delivered
        mark associated pet as sold
    send delivery confirmation
    return order
```

### OrderCancellationProcessor
**Entity**: Order  
**Input**: Order entity and cancellation reason  
**Purpose**: Cancels order and releases resources  
**Output**: Order entity with CANCELLED state  
**Transition**: Pet entities to AVAILABLE state, OrderItem entities to CANCELLED state

**Pseudocode**:
```
process(order, cancellationReason):
    record cancellation reason
    for each order item:
        cancel order item
        release associated pet reservation
        return pet to available status
    process refund if payment was made
    send cancellation notification
    return order
```

## OrderItem Processors

### OrderItemCreationProcessor
**Entity**: OrderItem  
**Input**: OrderItem entity  
**Purpose**: Creates and validates order item  
**Output**: OrderItem entity with PENDING state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(orderItem):
    validate pet exists
    validate quantity is positive
    get current pet price
    set orderItem.unitPrice to current price
    calculate orderItem.totalPrice
    return orderItem
```

### OrderItemConfirmationProcessor
**Entity**: OrderItem  
**Input**: OrderItem entity  
**Purpose**: Confirms order item for processing  
**Output**: OrderItem entity with CONFIRMED state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(orderItem):
    validate associated pet is still available
    confirm pricing is still valid
    lock inventory for this item
    return orderItem
```

### OrderItemDeliveryProcessor
**Entity**: OrderItem  
**Input**: OrderItem entity  
**Purpose**: Marks order item as delivered  
**Output**: OrderItem entity with DELIVERED state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(orderItem):
    validate item is ready for delivery
    record delivery timestamp
    update inventory records
    return orderItem
```

### OrderItemCancellationProcessor
**Entity**: OrderItem  
**Input**: OrderItem entity and cancellation reason  
**Purpose**: Cancels order item  
**Output**: OrderItem entity with CANCELLED state  
**Transition**: Pet entity to AVAILABLE state

**Pseudocode**:
```
process(orderItem, cancellationReason):
    record cancellation reason
    release pet reservation
    return pet to available inventory
    calculate refund amount
    return orderItem
```

## Address Processors

### AddressValidationProcessor
**Entity**: Address  
**Input**: Address entity  
**Purpose**: Validates address information  
**Output**: Address entity with ACTIVE state  
**Transition**: null (state change handled by workflow)

**Pseudocode**:
```
process(address):
    validate address.street is not empty
    validate address.city is not empty
    validate address.zipCode format
    validate address.country exists
    normalize address format
    return address
```
