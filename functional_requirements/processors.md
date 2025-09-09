# Purrfect Pets API - Processor Requirements

## Overview
This document defines the detailed requirements for all processors in the Purrfect Pets API system. Each processor implements specific business logic for workflow transitions.

## Pet Processors

### 1. PetInitializeProcessor

**Entity**: Pet  
**Transition**: none → available  
**Input**: Pet entity with basic information  
**Description**: Initialize a new pet and prepare it for availability

**Pseudocode**:
```
process(pet_entity):
    validate_required_fields(pet_entity.name, pet_entity.photoUrls)
    if pet_entity.price is null:
        pet_entity.price = 0.0
    if pet_entity.category is null:
        pet_entity.category = get_default_category()
    pet_entity.createdAt = current_timestamp()
    pet_entity.updatedAt = current_timestamp()
    pet_entity.vaccinated = pet_entity.vaccinated or false
    pet_entity.neutered = pet_entity.neutered or false
    
    log_info("Pet initialized: " + pet_entity.name)
    return pet_entity
```

**Expected Output**: Pet entity ready for availability with all default values set

### 2. PetReserveProcessor

**Entity**: Pet  
**Transition**: available → pending  
**Input**: Pet entity and order information  
**Description**: Reserve a pet when an order is placed

**Pseudocode**:
```
process(pet_entity):
    order_id = get_context_parameter("orderId")
    user_id = get_context_parameter("userId")
    
    validate_pet_available(pet_entity)
    validate_order_exists(order_id)
    
    pet_entity.reservedBy = user_id
    pet_entity.reservedAt = current_timestamp()
    pet_entity.reservedForOrder = order_id
    pet_entity.updatedAt = current_timestamp()
    
    send_notification("Pet reserved", user_id)
    log_info("Pet reserved: " + pet_entity.name + " for order: " + order_id)
    
    return pet_entity
```

**Expected Output**: Pet entity with reservation information  
**Other Entity Updates**: None

### 3. PetSaleProcessor

**Entity**: Pet  
**Transition**: pending → sold  
**Input**: Pet entity with reservation details  
**Description**: Complete the sale of a pet

**Pseudocode**:
```
process(pet_entity):
    order_id = pet_entity.reservedForOrder
    order = get_order_by_id(order_id)
    
    validate_order_approved(order)
    validate_payment_confirmed(order)
    
    pet_entity.soldAt = current_timestamp()
    pet_entity.soldTo = pet_entity.reservedBy
    pet_entity.salePrice = pet_entity.price
    pet_entity.updatedAt = current_timestamp()
    
    update_inventory_count(pet_entity.category.id, -1)
    send_notification("Pet sold successfully", pet_entity.soldTo)
    log_info("Pet sold: " + pet_entity.name + " to user: " + pet_entity.soldTo)
    
    return pet_entity
```

**Expected Output**: Pet entity marked as sold  
**Other Entity Updates**: Update Order to "delivered" state (transition: deliver_order)

### 4. PetCancelReservationProcessor

**Entity**: Pet  
**Transition**: pending → available  
**Input**: Pet entity with reservation details  
**Description**: Cancel pet reservation and make it available again

**Pseudocode**:
```
process(pet_entity):
    previous_user = pet_entity.reservedBy
    previous_order = pet_entity.reservedForOrder
    
    pet_entity.reservedBy = null
    pet_entity.reservedAt = null
    pet_entity.reservedForOrder = null
    pet_entity.updatedAt = current_timestamp()
    
    send_notification("Pet reservation cancelled", previous_user)
    log_info("Pet reservation cancelled: " + pet_entity.name)
    
    return pet_entity
```

**Expected Output**: Pet entity available for new reservations  
**Other Entity Updates**: None

## Order Processors

### 5. OrderPlaceProcessor

**Entity**: Order  
**Transition**: none → placed  
**Input**: Order entity with pet and user information  
**Description**: Place a new order for a pet

**Pseudocode**:
```
process(order_entity):
    validate_required_fields(order_entity.petId, order_entity.userId, order_entity.quantity)
    
    pet = get_pet_by_id(order_entity.petId)
    user = get_user_by_id(order_entity.userId)
    
    validate_pet_available(pet)
    validate_user_active(user)
    
    order_entity.totalAmount = pet.price * order_entity.quantity
    order_entity.paymentStatus = "pending"
    order_entity.complete = false
    order_entity.createdAt = current_timestamp()
    order_entity.updatedAt = current_timestamp()
    
    if order_entity.shipDate is null:
        order_entity.shipDate = current_timestamp() + 7_days
    
    log_info("Order placed: " + order_entity.id + " for pet: " + order_entity.petId)
    
    return order_entity
```

**Expected Output**: Order entity with calculated totals and dates  
**Other Entity Updates**: Update Pet to "pending" state (transition: reserve_pet)

### 6. OrderApprovalProcessor

**Entity**: Order  
**Transition**: placed → approved  
**Input**: Order entity with payment information  
**Description**: Approve order after validation

**Pseudocode**:
```
process(order_entity):
    validate_payment_method(order_entity.paymentMethod)
    validate_shipping_address(order_entity.shippingAddress)
    
    payment_result = process_payment(order_entity.totalAmount, order_entity.paymentMethod)
    
    if payment_result.success:
        order_entity.paymentStatus = "paid"
        order_entity.updatedAt = current_timestamp()
        
        send_notification("Order approved", order_entity.userId)
        send_email_confirmation(order_entity)
        log_info("Order approved: " + order_entity.id)
    else:
        order_entity.paymentStatus = "failed"
        log_error("Payment failed for order: " + order_entity.id)
    
    return order_entity
```

**Expected Output**: Order entity with payment status updated  
**Other Entity Updates**: None

### 7. OrderDeliveryProcessor

**Entity**: Order  
**Transition**: approved → delivered  
**Input**: Order entity ready for delivery  
**Description**: Mark order as delivered

**Pseudocode**:
```
process(order_entity):
    validate_order_approved(order_entity)
    
    order_entity.complete = true
    order_entity.deliveredAt = current_timestamp()
    order_entity.updatedAt = current_timestamp()
    
    send_notification("Order delivered", order_entity.userId)
    send_delivery_confirmation(order_entity)
    update_user_order_history(order_entity.userId, order_entity.id)
    
    log_info("Order delivered: " + order_entity.id)
    
    return order_entity
```

**Expected Output**: Order entity marked as complete and delivered  
**Other Entity Updates**: Update Pet to "sold" state (transition: complete_sale)

### 8. OrderCancelProcessor

**Entity**: Order  
**Transition**: placed/approved → cancelled  
**Input**: Order entity to be cancelled  
**Description**: Cancel an order and process refunds if needed

**Pseudocode**:
```
process(order_entity):
    cancellation_reason = get_context_parameter("reason")
    
    if order_entity.paymentStatus == "paid":
        refund_result = process_refund(order_entity.totalAmount, order_entity.paymentMethod)
        if refund_result.success:
            order_entity.paymentStatus = "refunded"
    
    order_entity.cancelledAt = current_timestamp()
    order_entity.cancellationReason = cancellation_reason
    order_entity.updatedAt = current_timestamp()
    
    send_notification("Order cancelled", order_entity.userId)
    log_info("Order cancelled: " + order_entity.id + " Reason: " + cancellation_reason)
    
    return order_entity
```

**Expected Output**: Order entity marked as cancelled with refund status  
**Other Entity Updates**: Update Pet to "available" state (transition: cancel_reservation)

## User Processors

### 9. UserRegistrationProcessor

**Entity**: User  
**Transition**: none → pending_verification  
**Input**: User entity with registration information  
**Description**: Register a new user account

**Pseudocode**:
```
process(user_entity):
    validate_required_fields(user_entity.username, user_entity.email, user_entity.password)
    validate_unique_username(user_entity.username)
    validate_unique_email(user_entity.email)
    validate_email_format(user_entity.email)
    
    user_entity.password = encrypt_password(user_entity.password)
    user_entity.createdAt = current_timestamp()
    user_entity.updatedAt = current_timestamp()
    
    if user_entity.preferences is null:
        user_entity.preferences = get_default_preferences()
    
    verification_token = generate_verification_token()
    user_entity.verificationToken = verification_token
    
    send_verification_email(user_entity.email, verification_token)
    log_info("User registered: " + user_entity.username)
    
    return user_entity
```

**Expected Output**: User entity with encrypted password and verification token  
**Other Entity Updates**: None

### 10. UserVerificationProcessor

**Entity**: User  
**Transition**: pending_verification → active  
**Input**: User entity with verification token  
**Description**: Verify user email and activate account

**Pseudocode**:
```
process(user_entity):
    verification_token = get_context_parameter("verificationToken")
    
    validate_verification_token(user_entity.verificationToken, verification_token)
    
    user_entity.emailVerified = true
    user_entity.verifiedAt = current_timestamp()
    user_entity.verificationToken = null
    user_entity.updatedAt = current_timestamp()
    
    send_welcome_email(user_entity.email)
    send_notification("Account activated", user_entity.id)
    log_info("User verified: " + user_entity.username)
    
    return user_entity
```

**Expected Output**: User entity with verified status  
**Other Entity Updates**: None

## Category Processors

### 11. CategoryCreateProcessor

**Entity**: Category  
**Transition**: none → active  
**Input**: Category entity with basic information  
**Description**: Create and activate a new category

**Pseudocode**:
```
process(category_entity):
    validate_required_fields(category_entity.name)
    validate_unique_category_name(category_entity.name)
    
    if category_entity.displayOrder is null:
        category_entity.displayOrder = get_next_display_order()
    
    category_entity.isActive = true
    category_entity.createdAt = current_timestamp()
    category_entity.updatedAt = current_timestamp()
    
    log_info("Category created: " + category_entity.name)
    
    return category_entity
```

**Expected Output**: Category entity ready for use  
**Other Entity Updates**: None

## Tag Processors

### 12. TagCreateProcessor

**Entity**: Tag  
**Transition**: none → active  
**Input**: Tag entity with basic information  
**Description**: Create and activate a new tag

**Pseudocode**:
```
process(tag_entity):
    validate_required_fields(tag_entity.name)
    validate_unique_tag_name(tag_entity.name)
    
    if tag_entity.color is null:
        tag_entity.color = generate_random_color()
    
    if tag_entity.category is null:
        tag_entity.category = "general"
    
    tag_entity.isActive = true
    tag_entity.createdAt = current_timestamp()
    tag_entity.updatedAt = current_timestamp()
    
    log_info("Tag created: " + tag_entity.name)
    
    return tag_entity
```

**Expected Output**: Tag entity ready for use  
**Other Entity Updates**: None

## Common Processor Patterns

### Validation Functions
- `validate_required_fields()`: Check for null/empty required fields
- `validate_unique_*()`: Check for uniqueness constraints
- `validate_*_format()`: Validate format (email, phone, etc.)
- `validate_*_exists()`: Check if referenced entities exist

### Utility Functions
- `current_timestamp()`: Get current date/time
- `generate_*()`: Generate tokens, IDs, colors, etc.
- `send_notification()`: Send in-app notifications
- `send_email_*()`: Send various email types
- `log_info/error()`: Logging functions
- `get_context_parameter()`: Get additional context data
