# Purrfect Pets API - Criteria Requirements

## Overview
This document defines the criteria for workflow transitions that require conditional logic. Criteria are used to validate conditions before allowing state transitions.

## Customer Criteria

### 1. CustomerSuspensionCriterion

**Entity**: Customer
**Transition**: suspend_account (verified → suspended)
**Purpose**: Validate that customer account can be suspended

**Validation Logic**:
- Customer must be in "verified" state
- Customer must not already be suspended
- Suspension reason must be provided
- Admin user performing suspension must have appropriate permissions

**Pseudocode**:
```
evaluate(customer_entity, input):
    // Check current state
    if customer.meta.state != "verified":
        return false, "Customer must be verified to suspend"
    
    // Check suspension reason
    if input.reason is null or input.reason.trim() is empty:
        return false, "Suspension reason is required"
    
    // Check admin permissions (if admin_user_id provided)
    if input.admin_user_id exists:
        admin = get_entity("Admin", input.admin_user_id)
        if not admin.can_suspend_customers:
            return false, "Admin does not have permission to suspend customers"
    
    // Check for active orders
    active_orders = get_entities_by_condition("Order", 
        "customer_id", customer.entity_id,
        "state", ["placed", "approved", "prepared"])
    
    if active_orders.count > 0:
        return false, "Cannot suspend customer with active orders"
    
    return true, "Customer can be suspended"
```

## Order Criteria

### 2. OrderApprovalCriterion

**Entity**: Order
**Transition**: approve_order (placed → approved)
**Purpose**: Validate that order can be approved

**Validation Logic**:
- Order must be in "placed" state
- Payment must be verified
- All pets in order must still be available/reserved
- Customer must still be verified
- Order total must match calculated total

**Pseudocode**:
```
evaluate(order_entity, input):
    // Check current state
    if order.meta.state != "placed":
        return false, "Order must be in placed state to approve"
    
    // Check payment verification
    if input.payment_verified != true:
        return false, "Payment must be verified before approval"
    
    if input.payment_reference is null or input.payment_reference.trim() is empty:
        return false, "Payment reference is required"
    
    // Validate customer is still verified
    customer = get_entity("Customer", order.customer_id)
    if customer.meta.state != "verified":
        return false, "Customer account is not verified"
    
    // Check all pets are still reserved
    order_items = get_entities_by_condition("OrderItem", "order_id", order.entity_id)
    for each item in order_items:
        pet = get_entity("Pet", item.pet_id)
        if pet.meta.state != "pending":
            return false, "Pet " + pet.name + " is no longer reserved"
    
    // Validate order total
    calculated_total = 0
    for each item in order_items:
        calculated_total += item.subtotal
    
    if abs(order.total_amount - calculated_total) > 0.01:
        return false, "Order total does not match calculated total"
    
    return true, "Order can be approved"
```

### 3. OrderShippingCriterion

**Entity**: Order
**Transition**: ship_order (prepared → shipped)
**Purpose**: Validate that order can be shipped

**Validation Logic**:
- Order must be in "prepared" state
- Shipping address must be complete
- Tracking number must be provided
- All order items must be prepared

**Pseudocode**:
```
evaluate(order_entity, input):
    // Check current state
    if order.meta.state != "prepared":
        return false, "Order must be prepared before shipping"
    
    // Validate shipping address
    if order.shipping_address is null:
        return false, "Shipping address is required"
    
    address = order.shipping_address
    if address.street is null or address.city is null or 
       address.state is null or address.zip_code is null:
        return false, "Complete shipping address is required"
    
    // Check tracking number
    if input.tracking_number is null or input.tracking_number.trim() is empty:
        return false, "Tracking number is required for shipping"
    
    // Check carrier
    if input.carrier is null or input.carrier.trim() is empty:
        return false, "Carrier information is required"
    
    // Validate all order items are prepared
    order_items = get_entities_by_condition("OrderItem", "order_id", order.entity_id)
    for each item in order_items:
        if item.meta.state != "prepared":
            return false, "All order items must be prepared before shipping"
    
    return true, "Order can be shipped"
```

## Pet Criteria

### 4. PetReservationCriterion

**Entity**: Pet
**Transition**: reserve_pet (available → pending)
**Purpose**: Validate that pet can be reserved

**Validation Logic**:
- Pet must be in "available" state
- Pet must not have any health issues that prevent sale
- Pet must have all required documentation

**Pseudocode**:
```
evaluate(pet_entity, input):
    // Check current state
    if pet.meta.state != "available":
        return false, "Pet must be available to reserve"
    
    // Check health status
    if pet.health_issues exists and pet.health_issues.length > 0:
        for each issue in pet.health_issues:
            if issue.severity == "critical":
                return false, "Pet has critical health issues and cannot be sold"
    
    // Check required documentation
    if pet.vaccination_status == false:
        return false, "Pet must be vaccinated before sale"
    
    // Check age restrictions (pets under 8 weeks cannot be sold)
    if pet.age < 8:
        return false, "Pet must be at least 8 weeks old for sale"
    
    // Check if pet has required photos
    if pet.photo_urls is null or pet.photo_urls.length == 0:
        return false, "Pet must have at least one photo"
    
    return true, "Pet can be reserved"
```

### 5. PetSaleCriterion

**Entity**: Pet
**Transition**: complete_sale (pending → sold)
**Purpose**: Validate that pet sale can be completed

**Validation Logic**:
- Pet must be in "pending" state
- Pet must have been reserved within valid timeframe
- Associated order must be delivered

**Pseudocode**:
```
evaluate(pet_entity, input):
    // Check current state
    if pet.meta.state != "pending":
        return false, "Pet must be pending to complete sale"
    
    // Check reservation timeframe
    if pet.reserved_at is null:
        return false, "Pet reservation timestamp is missing"
    
    reservation_age = current_timestamp() - pet.reserved_at
    if reservation_age > 7_days:
        return false, "Pet reservation has expired"
    
    // Find associated order
    order_items = get_entities_by_condition("OrderItem", "pet_id", pet.entity_id)
    if order_items.length == 0:
        return false, "No order found for this pet"
    
    // Check if order is delivered
    for each item in order_items:
        order = get_entity("Order", item.order_id)
        if order.meta.state != "delivered":
            return false, "Associated order must be delivered before completing sale"
    
    return true, "Pet sale can be completed"
```

## Category Criteria

### 6. CategoryDeactivationCriterion

**Entity**: Category
**Transition**: deactivate_category (active → inactive)
**Purpose**: Validate that category can be deactivated

**Validation Logic**:
- Category must be in "active" state
- Category should not have pending orders for its pets
- Admin confirmation required for categories with many pets

**Pseudocode**:
```
evaluate(category_entity, input):
    // Check current state
    if category.meta.state != "active":
        return false, "Category must be active to deactivate"
    
    // Check for pets with pending orders
    pets = get_entities_by_condition("Pet", "category_id", category.entity_id)
    for each pet in pets:
        if pet.meta.state == "pending":
            return false, "Cannot deactivate category with reserved pets"
    
    // Check for admin confirmation if category has many pets
    if pets.length > 10:
        if input.admin_confirmed != true:
            return false, "Admin confirmation required for categories with more than 10 pets"
    
    return true, "Category can be deactivated"
```

## OrderItem Criteria

### 7. OrderItemConfirmationCriterion

**Entity**: OrderItem
**Transition**: confirm_item (pending → confirmed)
**Purpose**: Validate that order item can be confirmed

**Validation Logic**:
- Order item must be in "pending" state
- Associated pet must still be reserved
- Order must be approved
- Pricing must be current

**Pseudocode**:
```
evaluate(order_item_entity, input):
    // Check current state
    if order_item.meta.state != "pending":
        return false, "Order item must be pending to confirm"
    
    // Check associated pet
    pet = get_entity("Pet", order_item.pet_id)
    if pet.meta.state != "pending":
        return false, "Associated pet is not reserved"
    
    // Check parent order
    order = get_entity("Order", order_item.order_id)
    if order.meta.state != "approved":
        return false, "Parent order must be approved"
    
    // Check pricing is still current
    if abs(order_item.unit_price - pet.price) > 0.01:
        return false, "Pet price has changed since order placement"
    
    return true, "Order item can be confirmed"
```

## Notes

1. **Return Format**: All criteria return a tuple of (boolean, string) where boolean indicates pass/fail and string provides the reason
2. **Error Messages**: Error messages should be user-friendly and specific to help with troubleshooting
3. **Performance**: Criteria should be lightweight and fast as they may be called frequently
4. **Dependencies**: Criteria can access other entities but should minimize external service calls
5. **Validation**: All input parameters should be validated before processing
6. **State Consistency**: Always verify entity states before applying business rules
