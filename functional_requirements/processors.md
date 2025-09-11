# Purrfect Pets API - Processor Requirements

## Overview
This document defines the processors for each entity workflow transition. Processors implement the business logic executed during state transitions.

## Pet Processors

### 1. PetInventoryProcessor

**Entity**: Pet
**Transition**: add_to_inventory (none → available)
**Input**: Pet entity with basic information
**Purpose**: Initialize pet in inventory system

**Pseudocode**:
```
process(pet_entity):
    // Validate required fields
    validate pet.name is not empty
    validate pet.price is positive number
    validate pet.photo_urls is not empty
    
    // Set default values
    if pet.age is null:
        set pet.age = 0
    if pet.vaccination_status is null:
        set pet.vaccination_status = false
    
    // Generate inventory tracking
    set pet.inventory_id = generate_unique_id()
    set pet.date_added = current_timestamp()
    
    // Update category pet count
    if pet.category_id exists:
        category = get_entity("Category", pet.category_id)
        increment category.pet_count
        update_entity(category, null)
    
    return pet_entity
```

### 2. PetReservationProcessor

**Entity**: Pet
**Transition**: reserve_pet (available → pending)
**Input**: Pet entity with reservation details
**Purpose**: Reserve pet for customer order

**Pseudocode**:
```
process(pet_entity):
    // Validate pet is still available
    validate pet.meta.state == "available"
    
    // Set reservation details
    set pet.reserved_at = current_timestamp()
    set pet.reservation_expires_at = current_timestamp() + 24_hours
    
    // Log reservation
    log_info("Pet reserved", pet.entity_id, pet.name)
    
    return pet_entity
```

### 3. PetSaleProcessor

**Entity**: Pet
**Transition**: complete_sale (pending → sold)
**Input**: Pet entity with sale completion details
**Purpose**: Finalize pet sale

**Pseudocode**:
```
process(pet_entity):
    // Validate pet is reserved
    validate pet.meta.state == "pending"
    
    // Set sale details
    set pet.sold_at = current_timestamp()
    set pet.final_sale_price = pet.price
    
    // Clear reservation data
    set pet.reserved_at = null
    set pet.reservation_expires_at = null
    
    // Update category statistics
    if pet.category_id exists:
        category = get_entity("Category", pet.category_id)
        increment category.pets_sold
        update_entity(category, null)
    
    return pet_entity
```

### 4. PetCancellationProcessor

**Entity**: Pet
**Transition**: cancel_reservation (pending → available)
**Input**: Pet entity with cancellation reason
**Purpose**: Cancel pet reservation and return to available status

**Pseudocode**:
```
process(pet_entity):
    // Validate pet is reserved
    validate pet.meta.state == "pending"
    
    // Clear reservation data
    set pet.reserved_at = null
    set pet.reservation_expires_at = null
    set pet.cancellation_reason = input.reason
    set pet.cancelled_at = current_timestamp()
    
    // Log cancellation
    log_info("Pet reservation cancelled", pet.entity_id, input.reason)
    
    return pet_entity
```

## Category Processors

### 5. CategoryActivationProcessor

**Entity**: Category
**Transition**: activate_category (none → active)
**Input**: Category entity with basic information
**Purpose**: Activate new category for public display

**Pseudocode**:
```
process(category_entity):
    // Validate required fields
    validate category.name is not empty
    
    // Set default values
    if category.display_order is null:
        set category.display_order = 999
    if category.is_featured is null:
        set category.is_featured = false
    
    // Initialize counters
    set category.pet_count = 0
    set category.pets_sold = 0
    set category.activated_at = current_timestamp()
    
    return category_entity
```

### 6. CategoryDeactivationProcessor

**Entity**: Category
**Transition**: deactivate_category (active → inactive)
**Input**: Category entity
**Purpose**: Deactivate category from public display

**Pseudocode**:
```
process(category_entity):
    // Set deactivation timestamp
    set category.deactivated_at = current_timestamp()
    
    // Hide all pets in this category from public listings
    pets = get_entities_by_condition("Pet", "category_id", category.entity_id)
    for each pet in pets:
        set pet.hidden_due_to_category = true
        update_entity(pet, null)
    
    return category_entity
```

### 7. CategoryReactivationProcessor

**Entity**: Category
**Transition**: reactivate_category (inactive → active)
**Input**: Category entity
**Purpose**: Reactivate previously deactivated category

**Pseudocode**:
```
process(category_entity):
    // Set reactivation timestamp
    set category.reactivated_at = current_timestamp()
    set category.deactivated_at = null
    
    // Restore visibility of pets in this category
    pets = get_entities_by_condition("Pet", "category_id", category.entity_id)
    for each pet in pets:
        set pet.hidden_due_to_category = false
        update_entity(pet, null)
    
    return category_entity
```

## Customer Processors

### 8. CustomerRegistrationProcessor

**Entity**: Customer
**Transition**: register_customer (none → registered)
**Input**: Customer entity with registration details
**Purpose**: Register new customer and initiate email verification

**Pseudocode**:
```
process(customer_entity):
    // Validate required fields
    validate customer.username is unique
    validate customer.email is valid format
    validate customer.email is unique
    
    // Generate verification token
    set customer.email_verification_token = generate_secure_token()
    set customer.email_verification_expires = current_timestamp() + 24_hours
    set customer.registered_at = current_timestamp()
    
    // Set default preferences
    if customer.preferences is null:
        set customer.preferences = {
            newsletter_subscription: false,
            preferred_pet_types: []
        }
    
    // Send verification email (external service call)
    send_verification_email(customer.email, customer.email_verification_token)
    
    return customer_entity
```

### 9. CustomerVerificationProcessor

**Entity**: Customer
**Transition**: verify_email (registered → verified)
**Input**: Customer entity with verification token
**Purpose**: Verify customer email address

**Pseudocode**:
```
process(customer_entity):
    // Validate verification token
    validate customer.email_verification_token == input.token
    validate current_timestamp() < customer.email_verification_expires
    
    // Complete verification
    set customer.email_verified = true
    set customer.email_verified_at = current_timestamp()
    set customer.email_verification_token = null
    set customer.email_verification_expires = null
    
    // Send welcome email
    send_welcome_email(customer.email, customer.first_name)
    
    return customer_entity
```

### 10. CustomerSuspensionProcessor

**Entity**: Customer
**Transition**: suspend_account (verified → suspended)
**Input**: Customer entity with suspension reason
**Purpose**: Suspend customer account for policy violations

**Pseudocode**:
```
process(customer_entity):
    // Set suspension details
    set customer.suspended_at = current_timestamp()
    set customer.suspension_reason = input.reason
    set customer.suspended_by = input.admin_user_id
    
    // Cancel any pending orders
    orders = get_entities_by_condition("Order", "customer_id", customer.entity_id)
    for each order in orders:
        if order.meta.state in ["placed", "approved"]:
            update_entity(order, "cancel_placed_order")
    
    // Send suspension notification
    send_suspension_email(customer.email, input.reason)
    
    return customer_entity
```

### 11. CustomerReactivationProcessor

**Entity**: Customer
**Transition**: reactivate_account (suspended → verified)
**Input**: Customer entity
**Purpose**: Reactivate suspended customer account

**Pseudocode**:
```
process(customer_entity):
    // Clear suspension details
    set customer.suspended_at = null
    set customer.suspension_reason = null
    set customer.suspended_by = null
    set customer.reactivated_at = current_timestamp()
    
    // Send reactivation notification
    send_reactivation_email(customer.email, customer.first_name)
    
    return customer_entity
```

### 12. CustomerDeletionProcessor

**Entity**: Customer
**Transition**: delete_account (verified/suspended → deleted)
**Input**: Customer entity
**Purpose**: Soft delete customer account and anonymize data

**Pseudocode**:
```
process(customer_entity):
    // Anonymize personal data
    set customer.first_name = "DELETED"
    set customer.last_name = "USER"
    set customer.email = "deleted_" + customer.entity_id + "@example.com"
    set customer.phone = null
    set customer.address = null
    set customer.date_of_birth = null
    set customer.deleted_at = current_timestamp()
    
    // Keep order history but anonymize
    orders = get_entities_by_condition("Order", "customer_id", customer.entity_id)
    for each order in orders:
        set order.customer_name = "Deleted User"
        update_entity(order, null)
    
    return customer_entity
```

## Order Processors

### 13. OrderPlacementProcessor

**Entity**: Order
**Transition**: place_order (none → placed)
**Input**: Order entity with order details and items
**Purpose**: Place new order and reserve pets

**Pseudocode**:
```
process(order_entity):
    // Validate customer exists and is verified
    customer = get_entity("Customer", order.customer_id)
    validate customer.meta.state == "verified"

    // Calculate total amount
    total = 0
    for each item in order.items:
        pet = get_entity("Pet", item.pet_id)
        validate pet.meta.state == "available"
        item.unit_price = pet.price
        item.subtotal = item.quantity * item.unit_price
        total += item.subtotal

        // Reserve the pet
        update_entity(pet, "reserve_pet")

    set order.total_amount = total
    set order.order_date = current_timestamp()

    // Create order items as separate entities
    for each item in order.items:
        create_entity("OrderItem", item, "create_order_item")

    return order_entity
```

### 14. OrderApprovalProcessor

**Entity**: Order
**Transition**: approve_order (placed → approved)
**Input**: Order entity with payment verification
**Purpose**: Approve order after payment verification

**Pseudocode**:
```
process(order_entity):
    // Verify payment
    validate input.payment_verified == true
    validate input.payment_reference is not empty

    // Set approval details
    set order.approved_at = current_timestamp()
    set order.payment_reference = input.payment_reference
    set order.approved_by = input.admin_user_id

    // Confirm all order items
    order_items = get_entities_by_condition("OrderItem", "order_id", order.entity_id)
    for each item in order_items:
        update_entity(item, "confirm_item")

    return order_entity
```

### 15. OrderPreparationProcessor

**Entity**: Order
**Transition**: prepare_order (approved → prepared)
**Input**: Order entity
**Purpose**: Prepare pets for shipping

**Pseudocode**:
```
process(order_entity):
    // Set preparation timestamp
    set order.preparation_started_at = current_timestamp()

    // Prepare all order items
    order_items = get_entities_by_condition("OrderItem", "order_id", order.entity_id)
    for each item in order_items:
        update_entity(item, "prepare_item")

    // Generate shipping label
    set order.shipping_label_id = generate_shipping_label(order.shipping_address)
    set order.prepared_at = current_timestamp()

    return order_entity
```

### 16. OrderShippingProcessor

**Entity**: Order
**Transition**: ship_order (prepared → shipped)
**Input**: Order entity with shipping details
**Purpose**: Ship order to customer

**Pseudocode**:
```
process(order_entity):
    // Set shipping details
    set order.ship_date = current_timestamp()
    set order.tracking_number = input.tracking_number
    set order.carrier = input.carrier

    // Ship all order items
    order_items = get_entities_by_condition("OrderItem", "order_id", order.entity_id)
    for each item in order_items:
        update_entity(item, "ship_item")

    // Send shipping notification
    customer = get_entity("Customer", order.customer_id)
    send_shipping_notification(customer.email, order.tracking_number)

    return order_entity
```

### 17. OrderDeliveryProcessor

**Entity**: Order
**Transition**: deliver_order (shipped → delivered)
**Input**: Order entity with delivery confirmation
**Purpose**: Confirm order delivery

**Pseudocode**:
```
process(order_entity):
    // Set delivery details
    set order.delivered_at = current_timestamp()
    set order.delivery_confirmation = input.delivery_confirmation

    // Mark all order items as delivered
    order_items = get_entities_by_condition("OrderItem", "order_id", order.entity_id)
    for each item in order_items:
        update_entity(item, "deliver_item")

        // Mark pets as sold
        pet = get_entity("Pet", item.pet_id)
        update_entity(pet, "complete_sale")

    // Send delivery confirmation
    customer = get_entity("Customer", order.customer_id)
    send_delivery_confirmation(customer.email, order.entity_id)

    return order_entity
```

### 18. OrderCancellationProcessor

**Entity**: Order
**Transition**: cancel_placed_order, cancel_approved_order (placed/approved → cancelled)
**Input**: Order entity with cancellation reason
**Purpose**: Cancel order and release reserved pets

**Pseudocode**:
```
process(order_entity):
    // Set cancellation details
    set order.cancelled_at = current_timestamp()
    set order.cancellation_reason = input.reason
    set order.cancelled_by = input.user_id

    // Release reserved pets
    order_items = get_entities_by_condition("OrderItem", "order_id", order.entity_id)
    for each item in order_items:
        pet = get_entity("Pet", item.pet_id)
        if pet.meta.state == "pending":
            update_entity(pet, "cancel_reservation")

    // Process refund if payment was made
    if order.meta.state == "approved":
        process_refund(order.payment_reference, order.total_amount)
        set order.refund_processed_at = current_timestamp()

    // Send cancellation notification
    customer = get_entity("Customer", order.customer_id)
    send_cancellation_notification(customer.email, order.entity_id, input.reason)

    return order_entity
```

## OrderItem Processors

### 19. OrderItemCreationProcessor

**Entity**: OrderItem
**Transition**: create_order_item (none → pending)
**Input**: OrderItem entity with item details
**Purpose**: Create order item when order is placed

**Pseudocode**:
```
process(order_item_entity):
    // Validate pet exists and is available
    pet = get_entity("Pet", order_item.pet_id)
    validate pet.meta.state == "available"

    // Set item details
    set order_item.unit_price = pet.price
    set order_item.subtotal = order_item.quantity * order_item.unit_price
    set order_item.created_at = current_timestamp()

    return order_item_entity
```

### 20. OrderItemConfirmationProcessor

**Entity**: OrderItem
**Transition**: confirm_item (pending → confirmed)
**Input**: OrderItem entity
**Purpose**: Confirm item availability and pricing

**Pseudocode**:
```
process(order_item_entity):
    // Verify pet is still reserved
    pet = get_entity("Pet", order_item.pet_id)
    validate pet.meta.state == "pending"

    // Set confirmation timestamp
    set order_item.confirmed_at = current_timestamp()

    return order_item_entity
```

### 21. OrderItemPreparationProcessor

**Entity**: OrderItem
**Transition**: prepare_item (confirmed → prepared)
**Input**: OrderItem entity
**Purpose**: Prepare individual pet for shipping

**Pseudocode**:
```
process(order_item_entity):
    // Set preparation details
    set order_item.preparation_started_at = current_timestamp()

    // Add special care instructions if needed
    pet = get_entity("Pet", order_item.pet_id)
    if pet.special_care_required:
        set order_item.care_instructions = pet.care_instructions

    set order_item.prepared_at = current_timestamp()

    return order_item_entity
```

### 22. OrderItemShippingProcessor

**Entity**: OrderItem
**Transition**: ship_item (prepared → shipped)
**Input**: OrderItem entity
**Purpose**: Ship individual item

**Pseudocode**:
```
process(order_item_entity):
    // Set shipping timestamp
    set order_item.shipped_at = current_timestamp()

    return order_item_entity
```

### 23. OrderItemDeliveryProcessor

**Entity**: OrderItem
**Transition**: deliver_item (shipped → delivered)
**Input**: OrderItem entity
**Purpose**: Confirm individual item delivery

**Pseudocode**:
```
process(order_item_entity):
    // Set delivery timestamp
    set order_item.delivered_at = current_timestamp()

    return order_item_entity
```
