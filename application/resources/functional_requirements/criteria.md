# Criteria for Purrfect Pets API

## Pet Criteria

### PetAvailabilityCriterion

**Entity:** Pet
**Purpose:** Check if pet is available for reservation
**Logic:** Verify pet state is Available and inventory has sufficient quantity

**Pseudocode:**
```
evaluate(pet):
    if pet.meta.state != "Available":
        return false
    inventory = get_inventory_by_pet_id(pet.id)
    if inventory.quantity - inventory.reserved_quantity <= 0:
        return false
    return true
```

### OrderCompletionCriterion

**Entity:** Pet (with order context)
**Purpose:** Check if associated order is completed
**Logic:** Verify the order containing this pet is in Delivered state

**Pseudocode:**
```
evaluate(pet, order_context):
    order = get_order_by_id(order_context.order_id)
    if order.meta.state == "Delivered":
        return true
    return false
```

## Category Criteria

### CategoryUsageCriterion

**Entity:** Category
**Purpose:** Check if category can be safely deactivated
**Logic:** Verify no pets are assigned to this category

**Pseudocode:**
```
evaluate(category):
    pet_count = count_pets_by_category_id(category.id)
    if pet_count > 0:
        return false
    return true
```

## User Criteria

### UserViolationCriterion

**Entity:** User
**Purpose:** Check if user has policy violations warranting suspension
**Logic:** Check for reported violations, fraudulent activities, or policy breaches

**Pseudocode:**
```
evaluate(user, violation_info):
    if violation_info.violation_type in ["FRAUD", "ABUSE", "SPAM"]:
        return true
    violation_count = get_user_violation_count(user.id)
    if violation_count >= 3:
        return true
    return false
```

### SuspensionReviewCriterion

**Entity:** User
**Purpose:** Check if suspended user can be reactivated
**Logic:** Verify admin approval and suspension period completion

**Pseudocode:**
```
evaluate(user, review_info):
    if review_info.admin_approved != true:
        return false
    suspension_log = get_latest_suspension(user.id)
    if suspension_log.minimum_period_days > 0:
        days_suspended = calculate_days_since(suspension_log.created_at)
        if days_suspended < suspension_log.minimum_period_days:
            return false
    return true
```

## Order Criteria

### OrderValidationCriterion

**Entity:** Order
**Purpose:** Validate order before approval
**Logic:** Check user validity, payment method, and order items availability

**Pseudocode:**
```
evaluate(order):
    user = get_user_by_id(order.user_id)
    if user.meta.state != "Active":
        return false
    if order.payment_method not in ["CREDIT_CARD", "DEBIT_CARD", "CASH", "BANK_TRANSFER"]:
        return false
    if order.total_amount <= 0:
        return false
    order_items = get_order_items_by_order_id(order.id)
    if order_items.size() == 0:
        return false
    for item in order_items:
        pet = get_pet_by_id(item.pet_id)
        if pet.meta.state != "Available":
            return false
    return true
```

### InventoryAvailabilityCriterion

**Entity:** Order
**Purpose:** Check if all order items are available in inventory
**Logic:** Verify sufficient inventory for all pets in the order

**Pseudocode:**
```
evaluate(order):
    order_items = get_order_items_by_order_id(order.id)
    for item in order_items:
        inventory = get_inventory_by_pet_id(item.pet_id)
        available_quantity = inventory.quantity - inventory.reserved_quantity
        if available_quantity < item.quantity:
            return false
    return true
```

### CancellationPolicyCriterion

**Entity:** Order
**Purpose:** Check if order can be cancelled based on policy
**Logic:** Verify cancellation is within allowed timeframe and order state

**Pseudocode:**
```
evaluate(order, cancellation_info):
    if order.meta.state not in ["Approved", "Preparing"]:
        return false
    hours_since_approval = calculate_hours_since(order.updated_at)
    if order.meta.state == "Approved" and hours_since_approval <= 24:
        return true
    if order.meta.state == "Preparing" and cancellation_info.admin_approved:
        return true
    return false
```

## OrderItem Criteria

### ItemAvailabilityCriterion

**Entity:** OrderItem
**Purpose:** Check if order item can be confirmed
**Logic:** Verify pet availability and inventory

**Pseudocode:**
```
evaluate(order_item):
    pet = get_pet_by_id(order_item.pet_id)
    if pet.meta.state != "Available":
        return false
    inventory = get_inventory_by_pet_id(order_item.pet_id)
    available_quantity = inventory.quantity - inventory.reserved_quantity
    if available_quantity < order_item.quantity:
        return false
    return true
```

### OrderItemCancellationCriterion

**Entity:** OrderItem
**Purpose:** Check if confirmed order item can be cancelled
**Logic:** Verify parent order allows item cancellation

**Pseudocode:**
```
evaluate(order_item):
    order = get_order_by_id(order_item.order_id)
    if order.meta.state in ["Shipped", "Delivered"]:
        return false
    return true
```

## Inventory Criteria

### LowStockCriterion

**Entity:** Inventory
**Purpose:** Check if inventory is below reorder level
**Logic:** Compare available quantity with reorder level

**Pseudocode:**
```
evaluate(inventory):
    available_quantity = inventory.quantity - inventory.reserved_quantity
    if available_quantity <= inventory.reorder_level and available_quantity > 0:
        return true
    return false
```

### OutOfStockCriterion

**Entity:** Inventory
**Purpose:** Check if inventory is completely out of stock
**Logic:** Verify available quantity is zero

**Pseudocode:**
```
evaluate(inventory):
    available_quantity = inventory.quantity - inventory.reserved_quantity
    if available_quantity <= 0:
        return true
    return false
```

### RestockCriterion

**Entity:** Inventory
**Purpose:** Check if inventory has been restocked sufficiently
**Logic:** Verify quantity is above reorder level

**Pseudocode:**
```
evaluate(inventory):
    available_quantity = inventory.quantity - inventory.reserved_quantity
    if available_quantity > inventory.reorder_level:
        return true
    return false
```

## Review Criteria

### ReviewModerationCriterion

**Entity:** Review
**Purpose:** Check if review meets approval standards
**Logic:** Validate review content and rating appropriateness

**Pseudocode:**
```
evaluate(review):
    if review.rating < 1 or review.rating > 5:
        return false
    if review.comment.length() > 1000:
        return false
    if contains_inappropriate_content(review.comment):
        return false
    return true
```

### ReviewViolationCriterion

**Entity:** Review
**Purpose:** Check if review violates community guidelines
**Logic:** Detect spam, offensive content, or fake reviews

**Pseudocode:**
```
evaluate(review):
    if contains_spam_keywords(review.comment):
        return true
    if contains_offensive_language(review.comment):
        return true
    if is_duplicate_review(review.user_id, review.pet_id):
        return true
    return false
```
