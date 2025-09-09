# Purrfect Pets API - Criteria Requirements

## Overview
This document defines the detailed requirements for all criteria in the Purrfect Pets API system. Criteria implement conditional logic to determine whether workflow transitions should occur.

## Pet Criteria

### 1. PetSaleCriterion

**Entity**: Pet  
**Transition**: pending → sold  
**Description**: Check if a pet sale can be completed

**Conditions**:
- Pet must be in "pending" state
- Associated order must exist and be in "approved" state
- Payment must be confirmed for the order
- Pet must still be reserved for the same order

**Pseudocode**:
```
evaluate(pet_entity) -> boolean:
    if pet_entity.meta.state != "pending":
        return false
    
    if pet_entity.reservedForOrder is null:
        return false
    
    order = get_order_by_id(pet_entity.reservedForOrder)
    if order is null:
        return false
    
    if order.meta.state != "approved":
        return false
    
    if order.paymentStatus != "paid":
        return false
    
    if order.petId != pet_entity.id:
        return false
    
    return true
```

**Expected Result**: Returns true if pet sale can be completed, false otherwise

## Order Criteria

### 2. OrderApprovalCriterion

**Entity**: Order  
**Transition**: placed → approved  
**Description**: Check if an order can be approved for processing

**Conditions**:
- Order must be in "placed" state
- Referenced pet must exist and be available or pending
- User must be active
- Payment method must be valid
- Shipping address must be complete
- Order total must be greater than 0

**Pseudocode**:
```
evaluate(order_entity) -> boolean:
    if order_entity.meta.state != "placed":
        return false
    
    if order_entity.totalAmount <= 0:
        return false
    
    pet = get_pet_by_id(order_entity.petId)
    if pet is null:
        return false
    
    if pet.meta.state not in ["available", "pending"]:
        return false
    
    user = get_user_by_id(order_entity.userId)
    if user is null or user.meta.state != "active":
        return false
    
    if not is_valid_payment_method(order_entity.paymentMethod):
        return false
    
    if not is_complete_address(order_entity.shippingAddress):
        return false
    
    return true
```

**Expected Result**: Returns true if order can be approved, false otherwise

### 3. OrderDeliveryCriterion

**Entity**: Order  
**Transition**: approved → delivered  
**Description**: Check if an order can be marked as delivered

**Conditions**:
- Order must be in "approved" state
- Payment must be confirmed
- Shipping date must have passed or be today
- Order must not already be complete

**Pseudocode**:
```
evaluate(order_entity) -> boolean:
    if order_entity.meta.state != "approved":
        return false
    
    if order_entity.paymentStatus != "paid":
        return false
    
    if order_entity.complete == true:
        return false
    
    current_date = current_date()
    if order_entity.shipDate > current_date:
        return false
    
    return true
```

**Expected Result**: Returns true if order can be delivered, false otherwise

## User Criteria

### 4. UserVerificationCriterion

**Entity**: User  
**Transition**: pending_verification → active  
**Description**: Check if a user can be verified and activated

**Conditions**:
- User must be in "pending_verification" state
- Verification token must be valid and not expired
- Email must not already be verified

**Pseudocode**:
```
evaluate(user_entity) -> boolean:
    if user_entity.meta.state != "pending_verification":
        return false
    
    if user_entity.emailVerified == true:
        return false
    
    if user_entity.verificationToken is null:
        return false
    
    if is_token_expired(user_entity.verificationToken):
        return false
    
    return true
```

**Expected Result**: Returns true if user can be verified, false otherwise

### 5. UserSuspensionCriterion

**Entity**: User  
**Transition**: active → suspended  
**Description**: Check if a user can be suspended

**Conditions**:
- User must be in "active" state
- User must not have any pending orders
- Suspension reason must be provided

**Pseudocode**:
```
evaluate(user_entity) -> boolean:
    if user_entity.meta.state != "active":
        return false
    
    suspension_reason = get_context_parameter("suspensionReason")
    if suspension_reason is null or suspension_reason.trim().isEmpty():
        return false
    
    pending_orders = get_orders_by_user_and_state(user_entity.id, "placed")
    if pending_orders.size() > 0:
        return false
    
    approved_orders = get_orders_by_user_and_state(user_entity.id, "approved")
    if approved_orders.size() > 0:
        return false
    
    return true
```

**Expected Result**: Returns true if user can be suspended, false otherwise

## Category Criteria

### 6. CategoryDeactivationCriterion

**Entity**: Category  
**Transition**: active → inactive  
**Description**: Check if a category can be deactivated

**Conditions**:
- Category must be in "active" state
- Category must not have any pets in "available" or "pending" states
- Category must not be a parent of other active categories

**Pseudocode**:
```
evaluate(category_entity) -> boolean:
    if category_entity.meta.state != "active":
        return false
    
    active_pets = get_pets_by_category_and_states(category_entity.id, ["available", "pending"])
    if active_pets.size() > 0:
        return false
    
    child_categories = get_categories_by_parent_id(category_entity.id)
    for child in child_categories:
        if child.meta.state == "active":
            return false
    
    return true
```

**Expected Result**: Returns true if category can be deactivated, false otherwise

## Tag Criteria

### 7. TagDeactivationCriterion

**Entity**: Tag  
**Transition**: active → inactive  
**Description**: Check if a tag can be deactivated

**Conditions**:
- Tag must be in "active" state
- Tag must not be associated with any pets in "available" or "pending" states

**Pseudocode**:
```
evaluate(tag_entity) -> boolean:
    if tag_entity.meta.state != "active":
        return false
    
    active_pets_with_tag = get_pets_by_tag_and_states(tag_entity.id, ["available", "pending"])
    if active_pets_with_tag.size() > 0:
        return false
    
    return true
```

**Expected Result**: Returns true if tag can be deactivated, false otherwise

## Business Rule Criteria

### 8. InventoryAvailabilityCriterion

**Description**: Check if there's sufficient inventory for an operation

**Pseudocode**:
```
evaluate(entity) -> boolean:
    if entity.type == "Order":
        pet = get_pet_by_id(entity.petId)
        if pet.meta.state != "available":
            return false
        
        requested_quantity = entity.quantity
        if requested_quantity > 1:
            // For this simple pet store, assume quantity is always 1
            return false
    
    return true
```

### 9. BusinessHoursCriterion

**Description**: Check if the operation is being performed during business hours

**Pseudocode**:
```
evaluate(entity) -> boolean:
    current_time = current_time()
    current_day = current_day_of_week()
    
    // Business hours: Monday-Friday 9AM-6PM, Saturday 10AM-4PM, Closed Sunday
    if current_day == "SUNDAY":
        return false
    
    if current_day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
        return current_time >= "09:00" and current_time <= "18:00"
    
    if current_day == "SATURDAY":
        return current_time >= "10:00" and current_time <= "16:00"
    
    return false
```

### 10. PaymentValidationCriterion

**Description**: Validate payment information and processing capability

**Pseudocode**:
```
evaluate(order_entity) -> boolean:
    payment_method = order_entity.paymentMethod
    
    if payment_method not in ["credit_card", "paypal", "bank_transfer"]:
        return false
    
    if payment_method == "credit_card":
        return validate_credit_card_info(order_entity)
    
    if payment_method == "paypal":
        return validate_paypal_account(order_entity.userId)
    
    if payment_method == "bank_transfer":
        return validate_bank_account_info(order_entity)
    
    return false
```

## Common Criteria Patterns

### Validation Helpers
- `is_valid_payment_method()`: Check if payment method is supported
- `is_complete_address()`: Validate shipping address completeness
- `is_token_expired()`: Check if verification token is still valid
- `validate_*_info()`: Validate specific data formats

### Data Access Helpers
- `get_*_by_id()`: Retrieve entities by ID
- `get_*_by_*_and_states()`: Get entities by criteria and states
- `get_orders_by_user_and_state()`: Get user orders in specific state

### Context Helpers
- `get_context_parameter()`: Get additional context data
- `current_time/date()`: Get current time/date information
- `current_day_of_week()`: Get current day for business rules

## Notes

1. **Error Handling**: All criteria should handle null values gracefully and return false for invalid states
2. **Performance**: Criteria should be lightweight and avoid complex database queries
3. **Logging**: Consider logging criteria evaluation results for debugging
4. **Context**: Use context parameters for additional data not available in the entity
5. **Business Rules**: Criteria can implement complex business rules that span multiple entities
