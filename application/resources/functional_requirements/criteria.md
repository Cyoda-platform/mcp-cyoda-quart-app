# Criteria Specification for Purrfect Pets API

## Overview
This document defines the criteria for validating conditions before allowing workflow transitions.

## Pet Criteria

### PetAvailabilityCriterion
**Entity**: Pet  
**Purpose**: Checks if pet is available for reservation or purchase  
**Input**: Pet entity  
**Output**: Boolean (true if available, false otherwise)

**Validation Logic**:
```
evaluate(pet):
    if pet.meta.state != AVAILABLE:
        return false
    if pet has active reservations:
        return false
    if pet is associated with pending orders:
        return false
    return true
```

### PetHealthCriterion
**Entity**: Pet  
**Purpose**: Validates pet health status before making available  
**Input**: Pet entity  
**Output**: Boolean (true if healthy, false otherwise)

**Validation Logic**:
```
evaluate(pet):
    if pet.vaccinated == false:
        return false
    if pet has health issues recorded:
        return false
    if pet requires medical attention:
        return false
    return true
```

## User Criteria

### UserVerificationCriterion
**Entity**: User  
**Purpose**: Validates user verification token and eligibility  
**Input**: User entity and verification token  
**Output**: Boolean (true if verification is valid, false otherwise)

**Validation Logic**:
```
evaluate(user, verificationToken):
    if verificationToken is null or empty:
        return false
    if verificationToken is expired:
        return false
    if verificationToken does not match user:
        return false
    if user.meta.state != PENDING_VERIFICATION:
        return false
    return true
```

### UserReinstateCheckCriterion
**Entity**: User  
**Purpose**: Checks if suspended user can be reinstated  
**Input**: User entity  
**Output**: Boolean (true if can be reinstated, false otherwise)

**Validation Logic**:
```
evaluate(user):
    if user.meta.state != SUSPENDED:
        return false
    if user has unresolved violations:
        return false
    if suspension period has not elapsed:
        return false
    if user has pending legal issues:
        return false
    return true
```

## Order Criteria

### OrderValidationCriterion
**Entity**: Order  
**Purpose**: Validates order before approval  
**Input**: Order entity  
**Output**: Boolean (true if valid for approval, false otherwise)

**Validation Logic**:
```
evaluate(order):
    if order.meta.state != PLACED:
        return false
    if order.userId is null:
        return false
    if user associated with order is not ACTIVE:
        return false
    if order has no items:
        return false
    for each order item:
        if associated pet is not available:
            return false
    if payment information is invalid:
        return false
    return true
```

### OrderCancellationCriterion
**Entity**: Order  
**Purpose**: Validates if approved order can be cancelled  
**Input**: Order entity  
**Output**: Boolean (true if can be cancelled, false otherwise)

**Validation Logic**:
```
evaluate(order):
    if order.meta.state != APPROVED:
        return false
    if order has items already shipped:
        return false
    if order is in delivery process:
        return false
    if cancellation window has expired:
        return false
    return true
```

## OrderItem Criteria

### OrderItemValidationCriterion
**Entity**: OrderItem  
**Purpose**: Validates order item before confirmation  
**Input**: OrderItem entity  
**Output**: Boolean (true if valid for confirmation, false otherwise)

**Validation Logic**:
```
evaluate(orderItem):
    if orderItem.meta.state != PENDING:
        return false
    if orderItem.petId is null:
        return false
    if associated pet is not in PENDING state:
        return false
    if orderItem.quantity <= 0:
        return false
    if orderItem.unitPrice <= 0:
        return false
    if associated order is not in PLACED state:
        return false
    return true
```

## General Validation Criteria

### EntityExistsCriterion
**Purpose**: Generic criterion to check if referenced entity exists  
**Input**: Entity ID and entity type  
**Output**: Boolean (true if exists, false otherwise)

**Validation Logic**:
```
evaluate(entityId, entityType):
    if entityId is null:
        return false
    entity = findById(entityId, entityType)
    if entity is null:
        return false
    return true
```

### UserPermissionCriterion
**Purpose**: Checks if user has permission to perform action  
**Input**: User entity, action type, target entity  
**Output**: Boolean (true if has permission, false otherwise)

**Validation Logic**:
```
evaluate(user, actionType, targetEntity):
    if user is null or user.meta.state != ACTIVE:
        return false
    
    switch actionType:
        case "CREATE_ORDER":
            return user.role in [CUSTOMER, STAFF, ADMIN]
        case "APPROVE_ORDER":
            return user.role in [STAFF, ADMIN]
        case "MANAGE_PETS":
            return user.role in [STAFF, ADMIN]
        case "MANAGE_USERS":
            return user.role == ADMIN
        case "VIEW_OWN_DATA":
            return targetEntity.userId == user.id or user.role in [STAFF, ADMIN]
        default:
            return false
```

### BusinessHoursCriterion
**Purpose**: Validates if action can be performed during business hours  
**Input**: Current timestamp  
**Output**: Boolean (true if within business hours, false otherwise)

**Validation Logic**:
```
evaluate(currentTime):
    businessStartHour = 9  // 9 AM
    businessEndHour = 18   // 6 PM
    
    currentHour = currentTime.getHour()
    dayOfWeek = currentTime.getDayOfWeek()
    
    if dayOfWeek in [SATURDAY, SUNDAY]:
        return false
    
    if currentHour < businessStartHour or currentHour >= businessEndHour:
        return false
    
    return true
```

### InventoryAvailabilityCriterion
**Purpose**: Checks inventory availability for pets  
**Input**: Pet entity  
**Output**: Boolean (true if available in inventory, false otherwise)

**Validation Logic**:
```
evaluate(pet):
    if pet is null:
        return false
    
    if pet.meta.state not in [AVAILABLE, PENDING]:
        return false
    
    if pet has quality issues:
        return false
    
    if pet is reserved by another customer:
        return false
    
    return true
```

### PaymentValidationCriterion
**Purpose**: Validates payment information for orders  
**Input**: Order entity with payment details  
**Output**: Boolean (true if payment is valid, false otherwise)

**Validation Logic**:
```
evaluate(order):
    if order.paymentMethod is null or empty:
        return false
    
    if order.totalAmount <= 0:
        return false
    
    switch order.paymentMethod:
        case "CREDIT_CARD":
            return validateCreditCard(order.paymentDetails)
        case "DEBIT_CARD":
            return validateDebitCard(order.paymentDetails)
        case "PAYPAL":
            return validatePayPal(order.paymentDetails)
        case "CASH":
            return true  // Cash payments are always valid
        default:
            return false
```

## Criteria Usage Notes

- All criteria return boolean values
- Criteria should be stateless and side-effect free
- Criteria are evaluated before processors are executed
- If a criterion returns false, the transition is blocked
- Criteria can access related entities through entity relationships
- Complex validation logic should be broken down into multiple simple criteria
- Criteria should log validation failures for debugging purposes
