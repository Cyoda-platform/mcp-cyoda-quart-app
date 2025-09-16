# Processors for Purrfect Pets API

## Pet Processors

### PetRegistrationProcessor

**Entity:** Pet
**Input Data:** Pet entity with basic information (name, category_id, photo_urls, tags, breed, age, weight, color, description, price, vaccination_status)
**What it does:** Validates and registers a new pet in the system
**Expected Output:** Pet entity with generated ID and timestamps, state set to Available

**Pseudocode:**
```
process(pet):
    validate pet.name is not empty and length <= 100
    validate pet.category_id exists in Category table
    validate pet.price >= 0
    validate pet.age >= 0 and age <= 50
    validate pet.weight > 0
    validate photo_urls are valid URLs
    set pet.created_at = current_timestamp
    set pet.updated_at = current_timestamp
    save pet to database
    create inventory record for pet with quantity = 1
    trigger InventoryInitializationProcessor for inventory (null transition)
    return pet
```

### PetReservationProcessor

**Entity:** Pet
**Input Data:** Pet entity, order information
**What it does:** Reserves a pet for an order
**Expected Output:** Pet entity with updated reservation status

**Pseudocode:**
```
process(pet, order_info):
    validate pet is in Available state
    validate order_info contains valid order_id
    update inventory to reserve 1 quantity for pet
    log reservation with order_id and timestamp
    return pet
```

### PetReleaseProcessor

**Entity:** Pet
**Input Data:** Pet entity, order cancellation information
**What it does:** Releases pet reservation when order is cancelled
**Expected Output:** Pet entity released from reservation

**Pseudocode:**
```
process(pet, cancellation_info):
    validate pet is in Pending state
    validate cancellation_info contains order_id
    update inventory to release reserved quantity
    log release with order_id and timestamp
    return pet
```

### PetSaleProcessor

**Entity:** Pet
**Input Data:** Pet entity, completed order information
**What it does:** Marks pet as sold when order is completed
**Expected Output:** Pet entity marked as sold

**Pseudocode:**
```
process(pet, order_info):
    validate pet is in Pending state
    validate order_info contains completed order_id
    update inventory to reduce available quantity by 1
    trigger InventoryUpdateProcessor for inventory (null transition)
    log sale with order_id, sale_date, and price
    return pet
```

## Category Processors

### CategoryActivationProcessor

**Entity:** Category
**Input Data:** Category entity with name and description
**What it does:** Activates a new category
**Expected Output:** Category entity with Active state

**Pseudocode:**
```
process(category):
    validate category.name is not empty and length <= 50
    validate category.name is unique
    set category.created_at = current_timestamp
    set category.updated_at = current_timestamp
    save category to database
    return category
```

### CategoryDeactivationProcessor

**Entity:** Category
**Input Data:** Category entity
**What it does:** Deactivates a category
**Expected Output:** Category entity with Inactive state

**Pseudocode:**
```
process(category):
    validate category is in Active state
    check if any pets are assigned to this category
    if pets exist, return error "Cannot deactivate category with assigned pets"
    set category.updated_at = current_timestamp
    return category
```

### CategoryReactivationProcessor

**Entity:** Category
**Input Data:** Category entity
**What it does:** Reactivates an inactive category
**Expected Output:** Category entity with Active state

**Pseudocode:**
```
process(category):
    validate category is in Inactive state
    set category.updated_at = current_timestamp
    return category
```

## User Processors

### UserRegistrationProcessor

**Entity:** User
**Input Data:** User entity with username, first_name, last_name, email, password, phone, address, user_type
**What it does:** Registers a new user in the system
**Expected Output:** User entity with encrypted password and Active state

**Pseudocode:**
```
process(user):
    validate user.username is unique and length <= 50
    validate user.email is valid format and unique
    validate user.password length >= 8
    validate user.first_name and last_name are not empty
    encrypt user.password using bcrypt
    set user.created_at = current_timestamp
    set user.updated_at = current_timestamp
    if user.user_type is empty, set to "CUSTOMER"
    save user to database
    send welcome email to user.email
    return user
```

### UserSuspensionProcessor

**Entity:** User
**Input Data:** User entity, suspension reason
**What it does:** Suspends a user account
**Expected Output:** User entity with Suspended state

**Pseudocode:**
```
process(user, suspension_info):
    validate user is in Active state
    validate suspension_info contains reason
    log suspension with reason, admin_id, and timestamp
    set user.updated_at = current_timestamp
    send suspension notification email to user.email
    return user
```

### UserDeactivationProcessor

**Entity:** User
**Input Data:** User entity
**What it does:** Deactivates a user account
**Expected Output:** User entity with Inactive state

**Pseudocode:**
```
process(user):
    validate user is in Active state
    cancel all pending orders for user
    trigger OrderCancellationProcessor for each pending order (OrderCancellation transition)
    set user.updated_at = current_timestamp
    send account deactivation email to user.email
    return user
```

### UserReactivationProcessor

**Entity:** User
**Input Data:** User entity, reactivation information
**What it does:** Reactivates a suspended or inactive user
**Expected Output:** User entity with Active state

**Pseudocode:**
```
process(user, reactivation_info):
    validate user is in Suspended or Inactive state
    if user was suspended, validate reactivation_info contains admin approval
    log reactivation with admin_id and timestamp
    set user.updated_at = current_timestamp
    send reactivation confirmation email to user.email
    return user
```

## Order Processors

### OrderCreationProcessor

**Entity:** Order
**Input Data:** Order entity with user_id, order items, shipping_address, payment_method
**What it does:** Creates a new order in the system
**Expected Output:** Order entity with generated ID and Placed state

**Pseudocode:**
```
process(order):
    validate order.user_id exists and user is Active
    validate order.shipping_address is not empty
    validate order.payment_method is valid
    calculate total_amount from order items
    set order.order_date = current_timestamp
    set order.created_at = current_timestamp
    set order.updated_at = current_timestamp
    save order to database
    for each order_item in order.items:
        trigger OrderItemAdditionProcessor (null transition)
    return order
```

### OrderApprovalProcessor

**Entity:** Order
**Input Data:** Order entity
**What it does:** Approves a valid order
**Expected Output:** Order entity with Approved state

**Pseudocode:**
```
process(order):
    validate order is in Placed state
    validate payment method and user details
    validate all order items are available
    reserve inventory for all order items
    for each order_item in order.items:
        pet = get_pet_by_id(order_item.pet_id)
        trigger PetReservationProcessor for pet (PetReservation transition)
    set order.updated_at = current_timestamp
    send order approval email to user
    return order
```

### OrderCancellationProcessor

**Entity:** Order
**Input Data:** Order entity, cancellation reason
**What it does:** Cancels an order and releases resources
**Expected Output:** Order entity with Cancelled state

**Pseudocode:**
```
process(order, cancellation_info):
    validate order can be cancelled based on current state
    release all reserved inventory
    for each order_item in order.items:
        pet = get_pet_by_id(order_item.pet_id)
        if pet.meta.state == "Pending":
            trigger PetReleaseProcessor for pet (PetRelease transition)
        trigger OrderItemCancellationProcessor for order_item (OrderItemCancellation transition)
    process refund if payment was made
    set order.updated_at = current_timestamp
    send cancellation confirmation email to user
    return order
```

### OrderPreparationProcessor

**Entity:** Order
**Input Data:** Order entity
**What it does:** Starts order preparation process
**Expected Output:** Order entity with Preparing state

**Pseudocode:**
```
process(order):
    validate order is in Approved state
    validate inventory availability for all items
    assign order to fulfillment team
    generate picking list
    set order.updated_at = current_timestamp
    send preparation notification to fulfillment team
    return order
```

### OrderShippingProcessor

**Entity:** Order
**Input Data:** Order entity, shipping information
**What it does:** Ships the prepared order
**Expected Output:** Order entity with Shipped state

**Pseudocode:**
```
process(order, shipping_info):
    validate order is in Preparing state
    validate shipping_info contains tracking details
    set order.ship_date = current_timestamp
    set order.updated_at = current_timestamp
    generate shipping label
    update inventory quantities (reduce by order quantities)
    for each order_item in order.items:
        pet = get_pet_by_id(order_item.pet_id)
        trigger PetSaleProcessor for pet (PetSale transition)
        inventory = get_inventory_by_pet_id(pet.id)
        trigger InventoryUpdateProcessor for inventory (null transition)
    send shipping notification with tracking to user
    return order
```

### OrderDeliveryProcessor

**Entity:** Order
**Input Data:** Order entity, delivery confirmation
**What it does:** Marks order as delivered
**Expected Output:** Order entity with Delivered state

**Pseudocode:**
```
process(order, delivery_info):
    validate order is in Shipped state
    validate delivery_info contains confirmation details
    set order.updated_at = current_timestamp
    log delivery confirmation with timestamp and recipient
    send delivery confirmation email to user
    trigger review request email after 24 hours
    return order
```

## OrderItem Processors

### OrderItemAdditionProcessor

**Entity:** OrderItem
**Input Data:** OrderItem entity with order_id, pet_id, quantity, unit_price
**What it does:** Adds an item to an order
**Expected Output:** OrderItem entity with Added state

**Pseudocode:**
```
process(order_item):
    validate order_item.order_id exists
    validate order_item.pet_id exists and pet is available
    validate order_item.quantity > 0
    calculate order_item.total_price = quantity * unit_price
    set order_item.created_at = current_timestamp
    set order_item.updated_at = current_timestamp
    save order_item to database
    update parent order total_amount
    return order_item
```

### OrderItemConfirmationProcessor

**Entity:** OrderItem
**Input Data:** OrderItem entity
**What it does:** Confirms item availability and pricing
**Expected Output:** OrderItem entity with Confirmed state

**Pseudocode:**
```
process(order_item):
    validate order_item is in Added state
    pet = get_pet_by_id(order_item.pet_id)
    validate pet is available and price matches
    inventory = get_inventory_by_pet_id(order_item.pet_id)
    validate sufficient inventory quantity
    set order_item.updated_at = current_timestamp
    return order_item
```

### OrderItemCancellationProcessor

**Entity:** OrderItem
**Input Data:** OrderItem entity, cancellation reason
**What it does:** Cancels an order item
**Expected Output:** OrderItem entity with Cancelled state

**Pseudocode:**
```
process(order_item, cancellation_info):
    validate order_item can be cancelled
    release any reserved inventory for this item
    update parent order total_amount (subtract item total)
    set order_item.updated_at = current_timestamp
    log cancellation with reason and timestamp
    return order_item
```

## Inventory Processors

### InventoryInitializationProcessor

**Entity:** Inventory
**Input Data:** Inventory entity with pet_id, initial quantity
**What it does:** Initializes inventory for a new pet
**Expected Output:** Inventory entity with InStock state

**Pseudocode:**
```
process(inventory):
    validate inventory.pet_id exists and is unique
    if inventory.quantity is null, set to 1
    set inventory.reserved_quantity = 0
    set inventory.reorder_level = 1
    set inventory.last_restocked = current_timestamp
    set inventory.created_at = current_timestamp
    set inventory.updated_at = current_timestamp
    save inventory to database
    return inventory
```

### InventoryUpdateProcessor

**Entity:** Inventory
**Input Data:** Inventory entity, quantity change information
**What it does:** Updates inventory quantities and checks stock levels
**Expected Output:** Inventory entity with updated quantities and appropriate state

**Pseudocode:**
```
process(inventory, update_info):
    if update_info.quantity_change != null:
        inventory.quantity += update_info.quantity_change
    if update_info.reserved_change != null:
        inventory.reserved_quantity += update_info.reserved_change
    validate inventory.quantity >= 0
    validate inventory.reserved_quantity >= 0
    set inventory.updated_at = current_timestamp
    available_quantity = inventory.quantity - inventory.reserved_quantity
    if available_quantity <= 0:
        trigger state transition to OutOfStock
    else if available_quantity <= inventory.reorder_level:
        trigger state transition to LowStock
    return inventory
```

### InventoryRestockProcessor

**Entity:** Inventory
**Input Data:** Inventory entity, restock information
**What it does:** Restocks inventory with new quantities
**Expected Output:** Inventory entity with updated quantities and InStock state

**Pseudocode:**
```
process(inventory, restock_info):
    validate restock_info.quantity > 0
    inventory.quantity += restock_info.quantity
    set inventory.last_restocked = current_timestamp
    set inventory.updated_at = current_timestamp
    log restock event with quantity and supplier info
    send restock notification to inventory manager
    return inventory
```

### InventoryDiscontinuationProcessor

**Entity:** Inventory
**Input Data:** Inventory entity, discontinuation reason
**What it does:** Marks inventory as discontinued
**Expected Output:** Inventory entity with Discontinued state

**Pseudocode:**
```
process(inventory, discontinuation_info):
    validate inventory is not in Discontinued state
    set inventory.quantity = 0
    set inventory.reserved_quantity = 0
    set inventory.updated_at = current_timestamp
    log discontinuation with reason and timestamp
    pet = get_pet_by_id(inventory.pet_id)
    update pet availability status
    return inventory
```

## Review Processors

### ReviewSubmissionProcessor

**Entity:** Review
**Input Data:** Review entity with pet_id, user_id, rating, comment
**What it does:** Submits a new review for moderation
**Expected Output:** Review entity with Pending state

**Pseudocode:**
```
process(review):
    validate review.pet_id exists
    validate review.user_id exists and user is Active
    validate review.rating is between 1 and 5
    validate review.comment length <= 1000
    check if user has already reviewed this pet
    if duplicate review exists, return error
    set review.helpful_count = 0
    set review.created_at = current_timestamp
    set review.updated_at = current_timestamp
    save review to database
    send review to moderation queue
    return review
```

### ReviewApprovalProcessor

**Entity:** Review
**Input Data:** Review entity, moderator information
**What it does:** Approves a review after moderation
**Expected Output:** Review entity with Approved state

**Pseudocode:**
```
process(review, moderation_info):
    validate review is in Pending state
    validate moderation_info contains moderator_id
    set review.updated_at = current_timestamp
    log approval with moderator_id and timestamp
    update pet average rating
    send approval notification to review author
    return review
```

### ReviewRejectionProcessor

**Entity:** Review
**Input Data:** Review entity, rejection reason
**What it does:** Rejects a review that violates guidelines
**Expected Output:** Review entity with Rejected state

**Pseudocode:**
```
process(review, rejection_info):
    validate review is in Pending state
    validate rejection_info contains reason and moderator_id
    set review.updated_at = current_timestamp
    log rejection with reason, moderator_id and timestamp
    send rejection notification to review author with reason
    return review
```
