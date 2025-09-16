# Purrfect Pets - Criteria Requirements

## Overview
This document defines the criteria for conditional logic in workflow transitions. Criteria determine whether a transition should be allowed based on current entity state or external conditions.

## Pet Criteria

### 1. PetCompleteCriterion
**Entity**: Pet  
**Purpose**: Check if pet information is complete and ready for availability  
**Used in**: DRAFT → AVAILABLE transition

**Logic**:
```
evaluate(pet):
    if pet.name is empty:
        return false, "Pet name is required"
    
    if pet.photoUrls is empty:
        return false, "At least one photo is required"
    
    if pet.price is null or pet.price <= 0:
        return false, "Valid price is required"
    
    if pet.category is null:
        return false, "Category is required"
    
    if pet.category.state != ACTIVE:
        return false, "Category must be active"
    
    for each tag in pet.tags:
        if tag.state != ACTIVE:
            return false, "All tags must be active"
    
    return true, "Pet information is complete"
```

### 2. PaymentCompleteCriterion
**Entity**: Pet (with order context)  
**Purpose**: Check if payment for the pet order is completed  
**Used in**: PENDING → SOLD transition

**Logic**:
```
evaluate(pet, orderContext):
    order = find order for pet
    
    if order is null:
        return false, "No associated order found"
    
    if order.paymentMethod is empty:
        return false, "Payment method not specified"
    
    paymentStatus = check payment gateway status for order
    
    if paymentStatus != "COMPLETED":
        return false, "Payment not completed"
    
    return true, "Payment completed successfully"
```

### 3. PetHealthCheckCriterion
**Entity**: Pet  
**Purpose**: Check if pet health information is current and valid  
**Used in**: UNAVAILABLE → AVAILABLE transition

**Logic**:
```
evaluate(pet):
    if pet.vaccinated is false:
        return false, "Pet must be vaccinated"
    
    lastHealthCheck = get last health check date for pet
    
    if lastHealthCheck is null or lastHealthCheck < (current date - 6 months):
        return false, "Recent health check required"
    
    if pet.age > 180 and pet.neutered is false:
        return false, "Older pets should be neutered/spayed"
    
    return true, "Pet health check passed"
```

## Category Criteria

### 1. CategoryEmptyCriterion
**Entity**: Category  
**Purpose**: Check if category has no associated pets  
**Used in**: INACTIVE → ARCHIVED transition

**Logic**:
```
evaluate(category):
    petCount = count pets where category = this category and state != ARCHIVED
    
    if petCount > 0:
        return false, "Category still has associated pets"
    
    return true, "Category is empty and can be archived"
```

## Tag Criteria

### 1. TagUnusedCriterion
**Entity**: Tag  
**Purpose**: Check if tag is not being used by any pets  
**Used in**: INACTIVE → ARCHIVED transition

**Logic**:
```
evaluate(tag):
    petCount = count pets where tags contains this tag and state != ARCHIVED
    
    if petCount > 0:
        return false, "Tag is still being used by pets"
    
    return true, "Tag is unused and can be archived"
```

## Order Criteria

### 1. PaymentValidCriterion
**Entity**: Order  
**Purpose**: Check if payment information is valid and can be processed  
**Used in**: PLACED → CONFIRMED transition

**Logic**:
```
evaluate(order):
    if order.paymentMethod is empty:
        return false, "Payment method is required"
    
    if order.totalAmount <= 0:
        return false, "Order total must be positive"
    
    user = get user by order.userId
    
    if user.state != ACTIVE:
        return false, "User account must be active"
    
    pet = get pet by order.petId
    
    if pet.state != AVAILABLE:
        return false, "Pet must be available for purchase"
    
    return true, "Payment information is valid"
```

### 2. CancellationAllowedCriterion
**Entity**: Order  
**Purpose**: Check if order can be cancelled  
**Used in**: CONFIRMED → CANCELLED transition

**Logic**:
```
evaluate(order):
    if order.state == PROCESSING or order.state == SHIPPED:
        return false, "Order cannot be cancelled after processing has started"
    
    timeSinceConfirmation = current time - order.updatedAt
    
    if timeSinceConfirmation > 2 hours:
        return false, "Order can only be cancelled within 2 hours of confirmation"
    
    return true, "Order can be cancelled"
```

### 3. ReturnEligibleCriterion
**Entity**: Order  
**Purpose**: Check if order is eligible for return  
**Used in**: DELIVERED → RETURNED transition

**Logic**:
```
evaluate(order):
    if order.shipDate is null:
        return false, "Order must have been shipped"
    
    timeSinceDelivery = current time - order.shipDate
    
    if timeSinceDelivery > 30 days:
        return false, "Return period has expired (30 days)"
    
    pet = get pet by order.petId
    
    if pet.age < 12: // Less than 1 year old
        if timeSinceDelivery > 7 days:
            return false, "Young pets can only be returned within 7 days"
    
    return true, "Order is eligible for return"
```

## User Criteria

### 1. SuspensionResolvedCriterion
**Entity**: User  
**Purpose**: Check if suspension reason has been resolved  
**Used in**: SUSPENDED → ACTIVE transition

**Logic**:
```
evaluate(user, resolutionData):
    suspensionReason = get suspension reason for user
    
    if suspensionReason == "PAYMENT_ISSUES":
        if resolutionData.paymentResolved != true:
            return false, "Payment issues must be resolved"
    
    if suspensionReason == "POLICY_VIOLATION":
        if resolutionData.acknowledgment != true:
            return false, "Policy violation acknowledgment required"
    
    if suspensionReason == "FRAUD_INVESTIGATION":
        if resolutionData.investigationComplete != true:
            return false, "Fraud investigation must be completed"
    
    return true, "Suspension reason has been resolved"
```

### 2. UserInactiveCriterion
**Entity**: User  
**Purpose**: Check if user has been inactive for sufficient time to archive  
**Used in**: DEACTIVATED → ARCHIVED transition

**Logic**:
```
evaluate(user):
    if user.lastLoginAt is null:
        timeSinceCreation = current time - user.createdAt
        if timeSinceCreation < 365 days:
            return false, "User must be inactive for at least 1 year"
    else:
        timeSinceLastLogin = current time - user.lastLoginAt
        if timeSinceLastLogin < 365 days:
            return false, "User must be inactive for at least 1 year"
    
    activeOrderCount = count orders where userId = user.id and state in (PLACED, CONFIRMED, PROCESSING, SHIPPED)
    
    if activeOrderCount > 0:
        return false, "User has active orders"
    
    return true, "User is eligible for archiving"
```

## Criteria Notes

1. **Return Values**: All criteria should return a boolean result and a descriptive message explaining the decision.

2. **Error Handling**: Criteria should handle null values and invalid data gracefully.

3. **Performance**: Criteria should be efficient as they may be called frequently during workflow transitions.

4. **External Dependencies**: Some criteria may need to check external systems (payment gateways, health records) and should handle failures appropriately.

5. **Business Rules**: Criteria implement business rules and should be easily configurable for different business requirements.

6. **Logging**: Important criteria decisions should be logged for audit purposes.
