# Purrfect Pets - Processor Requirements

## Overview
This document defines the processors for business logic in the Purrfect Pets API application. Each processor implements the business logic for specific workflow transitions.

## Pet Processors

### 1. PetCreationProcessor
**Entity**: Pet  
**Input**: New pet data  
**Purpose**: Initialize a new pet record and set up basic information  
**Output**: Pet entity with DRAFT state  
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(pet):
    validate required fields (name, photoUrls)
    set default values for optional fields
    generate unique pet ID
    set createdAt and updatedAt timestamps
    set initial price if not provided
    return updated pet entity
```

### 2. PetValidationProcessor
**Entity**: Pet  
**Input**: Pet in DRAFT state  
**Purpose**: Validate pet information is complete and ready for availability  
**Output**: Pet entity with AVAILABLE state  
**Transition**: DRAFT → AVAILABLE

**Pseudocode**:
```
process(pet):
    validate all required fields are present
    validate price is positive
    validate age is reasonable (0-300 months)
    validate weight is positive if provided
    validate photo URLs are accessible
    validate category exists and is active
    validate all tags exist and are active
    set updatedAt timestamp
    return updated pet entity
```

### 3. PetReservationProcessor
**Entity**: Pet  
**Input**: Pet in AVAILABLE state with order information  
**Purpose**: Reserve pet for a pending order  
**Output**: Pet entity with PENDING state  
**Transition**: AVAILABLE → PENDING

**Pseudocode**:
```
process(pet, orderData):
    validate order information is complete
    validate user exists and is active
    create new order entity with PLACED state
    trigger order workflow transition to CONFIRMED
    set pet updatedAt timestamp
    return updated pet entity
```

### 4. PetSaleProcessor
**Entity**: Pet  
**Input**: Pet in PENDING state with payment confirmation  
**Purpose**: Complete the sale of a pet  
**Output**: Pet entity with SOLD state  
**Transition**: PENDING → SOLD

**Pseudocode**:
```
process(pet, paymentData):
    validate payment is completed
    update associated order to PROCESSING state
    trigger order workflow transition to PROCESSING
    set pet sale date
    set pet updatedAt timestamp
    send confirmation email to customer
    return updated pet entity
```

### 5. PetReleaseProcessor
**Entity**: Pet  
**Input**: Pet in PENDING state  
**Purpose**: Release pet from pending status back to available  
**Output**: Pet entity with AVAILABLE state  
**Transition**: PENDING → AVAILABLE

**Pseudocode**:
```
process(pet):
    find associated pending order
    cancel the order (trigger order workflow to CANCELLED)
    clear any reservation data
    set pet updatedAt timestamp
    return updated pet entity
```

### 6. PetReactivationProcessor
**Entity**: Pet  
**Input**: Pet in UNAVAILABLE state  
**Purpose**: Reactivate an unavailable pet  
**Output**: Pet entity with AVAILABLE state  
**Transition**: UNAVAILABLE → AVAILABLE

**Pseudocode**:
```
process(pet):
    validate pet health information is current
    validate pet is still in good condition
    update any changed information
    set pet updatedAt timestamp
    return updated pet entity
```

### 7. PetArchiveProcessor
**Entity**: Pet  
**Input**: Pet in SOLD state  
**Purpose**: Archive a sold pet record  
**Output**: Pet entity with ARCHIVED state  
**Transition**: SOLD → ARCHIVED

**Pseudocode**:
```
process(pet):
    validate pet has been sold for sufficient time
    validate all associated orders are completed
    set archive date
    set pet updatedAt timestamp
    return updated pet entity
```

## Category Processors

### 1. CategoryCreationProcessor
**Entity**: Category  
**Input**: New category data  
**Purpose**: Initialize a new category record  
**Output**: Category entity with ACTIVE state  
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(category):
    validate required fields (name)
    check for duplicate category names
    generate unique category ID
    set createdAt and updatedAt timestamps
    set default description if not provided
    return updated category entity
```

### 2. CategoryReactivationProcessor
**Entity**: Category  
**Input**: Category in INACTIVE state  
**Purpose**: Reactivate an inactive category  
**Output**: Category entity with ACTIVE state  
**Transition**: INACTIVE → ACTIVE

**Pseudocode**:
```
process(category):
    validate category information is still relevant
    set updatedAt timestamp
    return updated category entity
```

### 3. CategoryArchiveProcessor
**Entity**: Category  
**Input**: Category in INACTIVE state  
**Purpose**: Archive a category that is no longer needed  
**Output**: Category entity with ARCHIVED state  
**Transition**: INACTIVE → ARCHIVED

**Pseudocode**:
```
process(category):
    validate no pets are currently using this category
    set archive date
    set updatedAt timestamp
    return updated category entity
```

## Tag Processors

### 1. TagCreationProcessor
**Entity**: Tag  
**Input**: New tag data  
**Purpose**: Initialize a new tag record  
**Output**: Tag entity with ACTIVE state  
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(tag):
    validate required fields (name)
    check for duplicate tag names
    generate unique tag ID
    set createdAt timestamp
    set default color if not provided
    return updated tag entity
```

### 2. TagArchiveProcessor
**Entity**: Tag
**Input**: Tag in INACTIVE state
**Purpose**: Archive a tag that is no longer used
**Output**: Tag entity with ARCHIVED state
**Transition**: INACTIVE → ARCHIVED

**Pseudocode**:
```
process(tag):
    validate no pets are currently using this tag
    set archive date
    return updated tag entity
```

## Order Processors

### 1. OrderCreationProcessor
**Entity**: Order
**Input**: New order data
**Purpose**: Initialize a new order record
**Output**: Order entity with PLACED state
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(order):
    validate required fields (userId, petId)
    validate user exists and is active
    validate pet exists and is available
    calculate total amount based on pet price and quantity
    generate unique order ID
    set orderDate to current timestamp
    set createdAt and updatedAt timestamps
    return updated order entity
```

### 2. OrderConfirmationProcessor
**Entity**: Order
**Input**: Order in PLACED state
**Purpose**: Confirm order and validate payment
**Output**: Order entity with CONFIRMED state
**Transition**: PLACED → CONFIRMED

**Pseudocode**:
```
process(order):
    validate payment information is complete
    process payment through payment gateway
    if payment successful:
        reserve the pet (trigger pet workflow to PENDING)
        send order confirmation email
        set updatedAt timestamp
    return updated order entity
```

### 3. OrderProcessingProcessor
**Entity**: Order
**Input**: Order in CONFIRMED state
**Purpose**: Begin processing the order
**Output**: Order entity with PROCESSING state
**Transition**: CONFIRMED → PROCESSING

**Pseudocode**:
```
process(order):
    validate pet is still reserved
    prepare pet for delivery (health check, grooming if needed)
    validate delivery address
    assign order to fulfillment team
    set updatedAt timestamp
    send processing notification to customer
    return updated order entity
```

### 4. OrderShippingProcessor
**Entity**: Order
**Input**: Order in PROCESSING state
**Purpose**: Ship the order
**Output**: Order entity with SHIPPED state
**Transition**: PROCESSING → SHIPPED

**Pseudocode**:
```
process(order, shippingData):
    validate shipping information
    generate tracking number
    set shipDate to current timestamp
    update pet status to SOLD (trigger pet workflow)
    send shipping notification with tracking info
    set updatedAt timestamp
    return updated order entity
```

### 5. OrderDeliveryProcessor
**Entity**: Order
**Input**: Order in SHIPPED state
**Purpose**: Mark order as delivered
**Output**: Order entity with DELIVERED state
**Transition**: SHIPPED → DELIVERED

**Pseudocode**:
```
process(order):
    validate delivery confirmation
    set delivery date
    send delivery confirmation to customer
    trigger customer satisfaction survey
    set updatedAt timestamp
    return updated order entity
```

### 6. OrderCancellationProcessor
**Entity**: Order
**Input**: Order in PLACED or CONFIRMED state
**Purpose**: Cancel an order
**Output**: Order entity with CANCELLED state
**Transition**: PLACED/CONFIRMED → CANCELLED

**Pseudocode**:
```
process(order, cancellationReason):
    if order is CONFIRMED:
        process refund
        release pet reservation (trigger pet workflow to AVAILABLE)
    record cancellation reason
    send cancellation confirmation to customer
    set updatedAt timestamp
    return updated order entity
```

### 7. OrderReturnProcessor
**Entity**: Order
**Input**: Order in DELIVERED state
**Purpose**: Process order return
**Output**: Order entity with RETURNED state
**Transition**: DELIVERED → RETURNED

**Pseudocode**:
```
process(order, returnData):
    validate return eligibility (time limit, condition)
    arrange pet pickup
    process refund
    update pet status back to AVAILABLE (trigger pet workflow)
    record return reason
    send return confirmation to customer
    set updatedAt timestamp
    return updated order entity
```

## User Processors

### 1. UserRegistrationProcessor
**Entity**: User
**Input**: New user registration data
**Purpose**: Initialize a new user account
**Output**: User entity with REGISTERED state
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(user):
    validate required fields (username, email, password)
    validate email format
    validate username uniqueness
    validate email uniqueness
    encrypt password
    generate unique user ID
    set createdAt and updatedAt timestamps
    send email verification link
    return updated user entity
```

### 2. UserVerificationProcessor
**Entity**: User
**Input**: User in REGISTERED state with verification token
**Purpose**: Verify user email address
**Output**: User entity with VERIFIED state
**Transition**: REGISTERED → VERIFIED

**Pseudocode**:
```
process(user, verificationToken):
    validate verification token
    check token expiration
    set emailVerified to true
    set updatedAt timestamp
    send welcome email
    return updated user entity
```

### 3. UserActivationProcessor
**Entity**: User
**Input**: User in VERIFIED state
**Purpose**: Activate user account
**Output**: User entity with ACTIVE state
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(user):
    set isActive to true
    set updatedAt timestamp
    send account activation confirmation
    return updated user entity
```

### 4. UserSuspensionProcessor
**Entity**: User
**Input**: User in ACTIVE state
**Purpose**: Suspend user account
**Output**: User entity with SUSPENDED state
**Transition**: ACTIVE → SUSPENDED

**Pseudocode**:
```
process(user, suspensionReason):
    set isActive to false
    record suspension reason
    cancel any pending orders
    send suspension notification
    set updatedAt timestamp
    return updated user entity
```

### 5. UserReactivationProcessor
**Entity**: User
**Input**: User in SUSPENDED or DEACTIVATED state
**Purpose**: Reactivate user account
**Output**: User entity with ACTIVE state
**Transition**: SUSPENDED/DEACTIVATED → ACTIVE

**Pseudocode**:
```
process(user):
    set isActive to true
    clear suspension/deactivation reason
    send reactivation confirmation
    set updatedAt timestamp
    return updated user entity
```

### 6. UserDeactivationProcessor
**Entity**: User
**Input**: User in ACTIVE state
**Purpose**: Deactivate user account
**Output**: User entity with DEACTIVATED state
**Transition**: ACTIVE → DEACTIVATED

**Pseudocode**:
```
process(user):
    set isActive to false
    cancel any pending orders
    send deactivation confirmation
    set updatedAt timestamp
    return updated user entity
```

### 7. UserArchiveProcessor
**Entity**: User
**Input**: User in DEACTIVATED state
**Purpose**: Archive user account
**Output**: User entity with ARCHIVED state
**Transition**: DEACTIVATED → ARCHIVED

**Pseudocode**:
```
process(user):
    validate user has been inactive for required period
    anonymize personal data (keep ID and basic info)
    set archive date
    set updatedAt timestamp
    return updated user entity
```

## Processor Notes

1. **Error Handling**: All processors should implement proper error handling and return meaningful error messages.

2. **Validation**: Input validation should be performed before any business logic execution.

3. **External Services**: Processors may call external services (payment gateways, email services, etc.) and should handle failures gracefully.

4. **Entity Updates**: Processors should always update the `updatedAt` timestamp when modifying entities.

5. **Workflow Triggers**: When processors need to trigger transitions in other entities, they should use the appropriate transition names or null for automatic transitions.
