# Purrfect Pets API - Processor Requirements

## Overview
This document defines the processors for business logic in the Purrfect Pets API system. Each processor implements the business logic for specific transitions.

## Pet Processors

### PetRegistrationProcessor
**Entity**: Pet  
**Input**: Pet entity with basic information  
**Purpose**: Registers a new pet in the system and makes it available for adoption  
**Output**: Pet entity with AVAILABLE state  
**Transition**: None (state change only)

**Pseudocode**:
```
process(pet):
    validate pet.name is not empty
    validate pet.categoryId exists in Category table
    set pet.createdAt to current timestamp
    set pet.updatedAt to current timestamp
    if pet.photoUrls is empty:
        set pet.photoUrls to default pet image for category
    save pet to database
    log "Pet registered: " + pet.name
    return pet
```

### PetReservationProcessor
**Entity**: Pet  
**Input**: Pet entity and reservation details (ownerId)  
**Purpose**: Reserves a pet for a potential adopter  
**Output**: Pet entity with RESERVED state, creates AdoptionApplication  
**Transition**: Create AdoptionApplication with SUBMITTED state

**Pseudocode**:
```
process(pet, ownerId):
    validate owner exists and is APPROVED
    validate pet is AVAILABLE
    create new AdoptionApplication:
        set ownerId = ownerId
        set petId = pet.id
        set applicationDate = current timestamp
        set state = SUBMITTED
    save AdoptionApplication
    set pet.updatedAt = current timestamp
    save pet
    send notification to owner about reservation
    log "Pet reserved: " + pet.name + " by owner: " + ownerId
    return pet
```

### PetAdoptionProcessor
**Entity**: Pet  
**Input**: Pet entity and adoption details  
**Purpose**: Finalizes pet adoption  
**Output**: Pet entity with ADOPTED state, updates related entities  
**Transition**: Update AdoptionApplication to APPROVED state

**Pseudocode**:
```
process(pet, adoptionDetails):
    find AdoptionApplication for this pet in APPROVED state
    validate application exists
    set pet.ownerId = application.ownerId
    set pet.updatedAt = current timestamp
    save pet
    update AdoptionApplication state to APPROVED
    create adoption record with adoption date and details
    send congratulations email to new owner
    send notification to staff about successful adoption
    log "Pet adopted: " + pet.name + " by owner: " + pet.ownerId
    return pet
```

### PetReservationCancellationProcessor
**Entity**: Pet  
**Input**: Pet entity  
**Purpose**: Cancels pet reservation and makes it available again  
**Output**: Pet entity with AVAILABLE state  
**Transition**: Update AdoptionApplication to WITHDRAWN state

**Pseudocode**:
```
process(pet):
    find active AdoptionApplication for this pet
    if application exists:
        update application state to WITHDRAWN
        save application
    set pet.updatedAt = current timestamp
    save pet
    send notification about cancellation
    log "Pet reservation cancelled: " + pet.name
    return pet
```

### PetMedicalHoldProcessor
**Entity**: Pet  
**Input**: Pet entity and medical hold reason  
**Purpose**: Places pet on medical hold  
**Output**: Pet entity with MEDICAL_HOLD state  
**Transition**: None

**Pseudocode**:
```
process(pet, medicalReason):
    set pet.medicalHoldReason = medicalReason
    set pet.medicalHoldDate = current timestamp
    set pet.updatedAt = current timestamp
    save pet
    notify veterinary staff
    log "Pet placed on medical hold: " + pet.name + " reason: " + medicalReason
    return pet
```

### PetMedicalClearanceProcessor
**Entity**: Pet  
**Input**: Pet entity and clearance details  
**Purpose**: Clears pet from medical hold  
**Output**: Pet entity with AVAILABLE state  
**Transition**: None

**Pseudocode**:
```
process(pet, clearanceDetails):
    validate clearance details are complete
    set pet.medicalClearanceDate = current timestamp
    set pet.medicalClearanceNotes = clearanceDetails.notes
    clear pet.medicalHoldReason
    set pet.updatedAt = current timestamp
    save pet
    log "Pet cleared from medical hold: " + pet.name
    return pet
```

## Category Processors

### CategoryActivationProcessor
**Entity**: Category  
**Input**: Category entity  
**Purpose**: Activates a new category  
**Output**: Category entity with ACTIVE state  
**Transition**: None

**Pseudocode**:
```
process(category):
    validate category.name is unique
    validate category.name is not empty
    set category.createdAt = current timestamp
    set category.updatedAt = current timestamp
    save category
    log "Category activated: " + category.name
    return category
```

## Owner Processors

### OwnerRegistrationProcessor
**Entity**: Owner  
**Input**: Owner entity with registration details  
**Purpose**: Registers a new owner in the system  
**Output**: Owner entity with REGISTERED state  
**Transition**: None

**Pseudocode**:
```
process(owner):
    validate owner.email is unique
    validate owner.email format is valid
    validate owner.firstName and lastName are not empty
    hash owner password if provided
    set owner.createdAt = current timestamp
    set owner.updatedAt = current timestamp
    save owner
    send welcome email to owner
    log "Owner registered: " + owner.email
    return owner
```

### OwnerVerificationProcessor
**Entity**: Owner  
**Input**: Owner entity  
**Purpose**: Verifies owner information  
**Output**: Owner entity with VERIFIED state  
**Transition**: None

**Pseudocode**:
```
process(owner):
    validate all required fields are present
    validate phone number format
    validate address information
    set owner.verificationDate = current timestamp
    set owner.updatedAt = current timestamp
    save owner
    send verification confirmation email
    log "Owner verified: " + owner.email
    return owner
```

### OwnerApprovalProcessor
**Entity**: Owner  
**Input**: Owner entity and approval details  
**Purpose**: Approves owner for pet adoptions  
**Output**: Owner entity with APPROVED state  
**Transition**: None

**Pseudocode**:
```
process(owner, approvalDetails):
    validate background check is complete
    validate references are checked
    set owner.approvalDate = current timestamp
    set owner.approvedBy = approvalDetails.staffMember
    set owner.approvalNotes = approvalDetails.notes
    set owner.updatedAt = current timestamp
    save owner
    send approval notification email
    log "Owner approved: " + owner.email
    return owner
```

### OwnerSuspensionProcessor
**Entity**: Owner  
**Input**: Owner entity and suspension reason  
**Purpose**: Suspends owner account  
**Output**: Owner entity with SUSPENDED state  
**Transition**: None

**Pseudocode**:
```
process(owner, suspensionReason):
    set owner.suspensionReason = suspensionReason
    set owner.suspensionDate = current timestamp
    set owner.updatedAt = current timestamp
    save owner
    cancel any pending adoption applications
    send suspension notification email
    log "Owner suspended: " + owner.email + " reason: " + suspensionReason
    return owner
```

### OwnerReinstateProcessor
**Entity**: Owner  
**Input**: Owner entity  
**Purpose**: Reinstates suspended owner  
**Output**: Owner entity with APPROVED state  
**Transition**: None

**Pseudocode**:
```
process(owner):
    clear owner.suspensionReason
    clear owner.suspensionDate
    set owner.reinstateDate = current timestamp
    set owner.updatedAt = current timestamp
    save owner
    send reinstatement notification email
    log "Owner reinstated: " + owner.email
    return owner
```

### OwnerReactivationProcessor
**Entity**: Owner  
**Input**: Owner entity  
**Purpose**: Reactivates inactive owner account  
**Output**: Owner entity with REGISTERED state  
**Transition**: None

**Pseudocode**:
```
process(owner):
    set owner.reactivationDate = current timestamp
    set owner.updatedAt = current timestamp
    save owner
    send reactivation welcome email
    log "Owner reactivated: " + owner.email
    return owner
```

## Order Processors

### OrderCreationProcessor
**Entity**: Order  
**Input**: Order entity with order details  
**Purpose**: Creates a new order  
**Output**: Order entity with PENDING state  
**Transition**: Create OrderItems with PENDING state

**Pseudocode**:
```
process(order):
    validate owner exists and is APPROVED
    validate order items are valid
    calculate total amount from order items
    set order.orderDate = current timestamp
    set order.createdAt = current timestamp
    set order.updatedAt = current timestamp
    save order
    for each item in order.items:
        create OrderItem with PENDING state
    send order confirmation email
    log "Order created: " + order.id + " for owner: " + order.ownerId
    return order
```

### OrderConfirmationProcessor
**Entity**: Order  
**Input**: Order entity and payment details  
**Purpose**: Confirms order after payment validation  
**Output**: Order entity with CONFIRMED state  
**Transition**: Update OrderItems to CONFIRMED state

**Pseudocode**:
```
process(order, paymentDetails):
    validate payment is successful
    set order.paymentMethod = paymentDetails.method
    set order.paymentConfirmationId = paymentDetails.confirmationId
    set order.updatedAt = current timestamp
    save order
    update all OrderItems to CONFIRMED state
    reserve any pets in the order
    send payment confirmation email
    log "Order confirmed: " + order.id
    return order
```

### OrderProcessingProcessor
**Entity**: Order  
**Input**: Order entity  
**Purpose**: Starts order processing  
**Output**: Order entity with PROCESSING state  
**Transition**: None

**Pseudocode**:
```
process(order):
    validate all items are available
    allocate inventory for order items
    generate picking list for warehouse
    set order.processingStartDate = current timestamp
    set order.updatedAt = current timestamp
    save order
    notify warehouse team
    log "Order processing started: " + order.id
    return order
```

### OrderShippingProcessor
**Entity**: Order  
**Input**: Order entity and shipping details  
**Purpose**: Ships the order  
**Output**: Order entity with SHIPPED state  
**Transition**: None

**Pseudocode**:
```
process(order, shippingDetails):
    validate all items are packed
    generate shipping label
    set order.shipDate = current timestamp
    set order.trackingNumber = shippingDetails.trackingNumber
    set order.shippingCarrier = shippingDetails.carrier
    set order.updatedAt = current timestamp
    save order
    send shipping notification email with tracking info
    log "Order shipped: " + order.id + " tracking: " + order.trackingNumber
    return order
```

### OrderDeliveryProcessor
**Entity**: Order  
**Input**: Order entity  
**Purpose**: Marks order as delivered  
**Output**: Order entity with DELIVERED state  
**Transition**: None

**Pseudocode**:
```
process(order):
    set order.deliveryDate = current timestamp
    set order.updatedAt = current timestamp
    save order
    send delivery confirmation email
    request customer feedback
    log "Order delivered: " + order.id
    return order
```

### OrderCancellationProcessor
**Entity**: Order  
**Input**: Order entity and cancellation reason  
**Purpose**: Cancels an order  
**Output**: Order entity with CANCELLED state  
**Transition**: Update OrderItems to CANCELLED state

**Pseudocode**:
```
process(order, cancellationReason):
    set order.cancellationReason = cancellationReason
    set order.cancellationDate = current timestamp
    set order.updatedAt = current timestamp
    save order
    update all OrderItems to CANCELLED state
    release any reserved pets
    release allocated inventory
    send cancellation notification email
    log "Order cancelled: " + order.id + " reason: " + cancellationReason
    return order
```

### OrderRefundProcessor
**Entity**: Order  
**Input**: Order entity and refund details  
**Purpose**: Processes refund for cancelled order  
**Output**: Order entity with REFUNDED state  
**Transition**: None

**Pseudocode**:
```
process(order, refundDetails):
    validate order is CANCELLED
    process refund through payment gateway
    set order.refundAmount = refundDetails.amount
    set order.refundDate = current timestamp
    set order.refundTransactionId = refundDetails.transactionId
    set order.updatedAt = current timestamp
    save order
    send refund confirmation email
    log "Order refunded: " + order.id + " amount: " + refundDetails.amount
    return order
```

## OrderItem Processors

### OrderItemCreationProcessor
**Entity**: OrderItem  
**Input**: OrderItem entity  
**Purpose**: Creates a new order item  
**Output**: OrderItem entity with PENDING state  
**Transition**: None

**Pseudocode**:
```
process(orderItem):
    validate product/pet exists
    validate quantity is positive
    calculate totalPrice = quantity * unitPrice
    set orderItem.createdAt = current timestamp
    save orderItem
    log "Order item created: " + orderItem.id
    return orderItem
```

## AdoptionApplication Processors

### AdoptionApplicationSubmissionProcessor
**Entity**: AdoptionApplication  
**Input**: AdoptionApplication entity  
**Purpose**: Submits a new adoption application  
**Output**: AdoptionApplication entity with SUBMITTED state  
**Transition**: None

**Pseudocode**:
```
process(application):
    validate owner exists and is APPROVED
    validate pet exists and is AVAILABLE
    validate required fields are complete
    set application.applicationDate = current timestamp
    set application.createdAt = current timestamp
    set application.updatedAt = current timestamp
    save application
    send application confirmation email
    notify staff about new application
    log "Adoption application submitted: " + application.id
    return application
```

### AdoptionApplicationReviewProcessor
**Entity**: AdoptionApplication  
**Input**: AdoptionApplication entity  
**Purpose**: Starts review process for adoption application  
**Output**: AdoptionApplication entity with UNDER_REVIEW state  
**Transition**: None

**Pseudocode**:
```
process(application):
    assign application to review staff
    set application.reviewStartDate = current timestamp
    set application.updatedAt = current timestamp
    save application
    send review started notification to applicant
    notify assigned reviewer
    log "Adoption application review started: " + application.id
    return application
```

### AdoptionApplicationApprovalProcessor
**Entity**: AdoptionApplication  
**Input**: AdoptionApplication entity and approval details  
**Purpose**: Approves adoption application  
**Output**: AdoptionApplication entity with APPROVED state  
**Transition**: Update Pet to RESERVED state

**Pseudocode**:
```
process(application, approvalDetails):
    validate all review criteria are met
    set application.reviewedBy = approvalDetails.reviewer
    set application.reviewNotes = approvalDetails.notes
    set application.approvalDate = current timestamp
    set application.updatedAt = current timestamp
    save application
    update Pet state to RESERVED
    send approval notification email
    schedule adoption appointment
    log "Adoption application approved: " + application.id
    return application
```

### AdoptionApplicationRejectionProcessor
**Entity**: AdoptionApplication  
**Input**: AdoptionApplication entity and rejection reason  
**Purpose**: Rejects adoption application  
**Output**: AdoptionApplication entity with REJECTED state  
**Transition**: None

**Pseudocode**:
```
process(application, rejectionReason):
    set application.rejectionReason = rejectionReason
    set application.rejectionDate = current timestamp
    set application.reviewedBy = current staff member
    set application.updatedAt = current timestamp
    save application
    send rejection notification email with reason
    log "Adoption application rejected: " + application.id + " reason: " + rejectionReason
    return application
```
