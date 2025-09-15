# Processors for Purrfect Pets API

## Pet Processors

### PetInitializationProcessor
**Entity:** Pet
**Input:** Pet entity with basic data
**Process:**
```
1. Set default values for optional fields
2. Generate unique ID if not provided
3. Set created_at timestamp
4. Initialize photo_urls as empty list if null
5. Initialize tags as empty list if null
6. Set default price to 0.0 if not provided
```
**Output:** Pet entity ready for validation
**Transition:** null (state managed by workflow)

### PetValidationProcessor
**Entity:** Pet
**Input:** Pet entity in DRAFT state
**Process:**
```
1. Validate required fields (name, category_id)
2. Validate price is positive
3. Validate age is positive if provided
4. Validate weight is positive if provided
5. Check if category exists and is active
6. Set updated_at timestamp
```
**Output:** Validated Pet entity
**Transition:** null (state managed by workflow)

### PetReservationProcessor
**Entity:** Pet
**Input:** Pet entity in AVAILABLE state
**Process:**
```
1. Mark pet as reserved
2. Set updated_at timestamp
3. Log reservation event
```
**Output:** Pet entity in PENDING state
**Transition:** null (state managed by workflow)

### PetSaleProcessor
**Entity:** Pet
**Input:** Pet entity in PENDING state
**Process:**
```
1. Mark pet as sold
2. Set updated_at timestamp
3. Log sale completion event
4. Update inventory metrics
```
**Output:** Pet entity in SOLD state
**Transition:** null (state managed by workflow)

### PetReleaseProcessor
**Entity:** Pet
**Input:** Pet entity in PENDING state
**Process:**
```
1. Release pet reservation
2. Set updated_at timestamp
3. Log release event
```
**Output:** Pet entity back to AVAILABLE state
**Transition:** null (state managed by workflow)

### PetUnavailableProcessor
**Entity:** Pet
**Input:** Pet entity in AVAILABLE state
**Process:**
```
1. Mark pet as unavailable
2. Set updated_at timestamp
3. Log unavailability reason
```
**Output:** Pet entity in UNAVAILABLE state
**Transition:** null (state managed by workflow)

### PetRestoreProcessor
**Entity:** Pet
**Input:** Pet entity in UNAVAILABLE state
**Process:**
```
1. Restore pet availability
2. Set updated_at timestamp
3. Log restoration event
```
**Output:** Pet entity back to AVAILABLE state
**Transition:** null (state managed by workflow)

## Category Processors

### CategoryInitializationProcessor
**Entity:** Category
**Input:** Category entity with basic data
**Process:**
```
1. Set default values for optional fields
2. Generate unique ID if not provided
3. Set created_at timestamp
4. Validate name uniqueness
```
**Output:** Category entity ready for activation
**Transition:** null (state managed by workflow)

### CategoryActivationProcessor
**Entity:** Category
**Input:** Category entity in DRAFT state
**Process:**
```
1. Validate category name is unique
2. Set updated_at timestamp
3. Log activation event
```
**Output:** Active Category entity
**Transition:** null (state managed by workflow)

### CategoryDeactivationProcessor
**Entity:** Category
**Input:** Category entity in ACTIVE state
**Process:**
```
1. Check if category has active pets
2. Set updated_at timestamp
3. Log deactivation event
```
**Output:** Category entity in INACTIVE state
**Transition:** null (state managed by workflow)

### CategoryReactivationProcessor
**Entity:** Category
**Input:** Category entity in INACTIVE state
**Process:**
```
1. Validate category can be reactivated
2. Set updated_at timestamp
3. Log reactivation event
```
**Output:** Category entity back to ACTIVE state
**Transition:** null (state managed by workflow)

## Customer Processors

### CustomerRegistrationProcessor
**Entity:** Customer
**Input:** Customer entity with registration data
**Process:**
```
1. Validate required fields (username, email, first_name, last_name)
2. Check username and email uniqueness
3. Generate unique ID if not provided
4. Set created_at timestamp
5. Send verification email
```
**Output:** Customer entity in PENDING_VERIFICATION state
**Transition:** null (state managed by workflow)

### CustomerVerificationProcessor
**Entity:** Customer
**Input:** Customer entity in PENDING_VERIFICATION state
**Process:**
```
1. Verify email confirmation
2. Set updated_at timestamp
3. Log verification completion
4. Send welcome email
```
**Output:** Customer entity in ACTIVE state
**Transition:** null (state managed by workflow)

### CustomerSuspensionProcessor
**Entity:** Customer
**Input:** Customer entity in ACTIVE state
**Process:**
```
1. Record suspension reason
2. Set updated_at timestamp
3. Cancel active orders if any
4. Send suspension notification
```
**Output:** Customer entity in SUSPENDED state
**Transition:** For active orders -> OrderCancellationProcessor

### CustomerReactivationProcessor
**Entity:** Customer
**Input:** Customer entity in SUSPENDED state
**Process:**
```
1. Validate reactivation conditions
2. Set updated_at timestamp
3. Log reactivation event
4. Send reactivation notification
```
**Output:** Customer entity back to ACTIVE state
**Transition:** null (state managed by workflow)

### CustomerDeactivationProcessor
**Entity:** Customer
**Input:** Customer entity in ACTIVE state
**Process:**
```
1. Archive customer data
2. Set updated_at timestamp
3. Cancel active orders if any
4. Log deactivation event
```
**Output:** Customer entity in INACTIVE state
**Transition:** For active orders -> OrderCancellationProcessor

## Order Processors

### OrderInitializationProcessor
**Entity:** Order
**Input:** Order entity with basic data
**Process:**
```
1. Generate unique ID if not provided
2. Set order_date to current timestamp
3. Set created_at timestamp
4. Initialize total_amount to 0.0
5. Validate customer exists and is active
```
**Output:** Order entity in DRAFT state
**Transition:** null (state managed by workflow)

### OrderPlacementProcessor
**Entity:** Order
**Input:** Order entity in DRAFT state
**Process:**
```
1. Calculate total amount from order items
2. Validate all pets are available
3. Reserve all pets in the order
4. Set updated_at timestamp
5. Send order confirmation email
```
**Output:** Order entity in PLACED state
**Transition:** For pets -> PetReservationProcessor

### OrderApprovalProcessor
**Entity:** Order
**Input:** Order entity in PLACED state
**Process:**
```
1. Validate payment information
2. Process payment
3. Set updated_at timestamp
4. Log approval event
```
**Output:** Order entity in APPROVED state
**Transition:** null (state managed by workflow)

### OrderShippingProcessor
**Entity:** Order
**Input:** Order entity in APPROVED state
**Process:**
```
1. Generate shipping label
2. Set ship_date timestamp
3. Update inventory
4. Send shipping notification
```
**Output:** Order entity in SHIPPED state
**Transition:** For pets -> PetSaleProcessor

### OrderDeliveryProcessor
**Entity:** Order
**Input:** Order entity in SHIPPED state
**Process:**
```
1. Confirm delivery
2. Set updated_at timestamp
3. Send delivery confirmation
4. Request customer feedback
```
**Output:** Order entity in DELIVERED state
**Transition:** null (state managed by workflow)

### OrderCancellationProcessor
**Entity:** Order
**Input:** Order entity in DRAFT or PLACED state
**Process:**
```
1. Release reserved pets if any
2. Process refund if payment was made
3. Set updated_at timestamp
4. Send cancellation notification
```
**Output:** Order entity in CANCELLED state
**Transition:** For pets -> PetReleaseProcessor

## OrderItem Processors

### OrderItemInitializationProcessor
**Entity:** OrderItem
**Input:** OrderItem entity with basic data
**Process:**
```
1. Generate unique ID if not provided
2. Validate pet exists and is available
3. Calculate total_price (quantity * unit_price)
4. Set created_at timestamp
```
**Output:** OrderItem entity in DRAFT state
**Transition:** null (state managed by workflow)

### OrderItemConfirmationProcessor
**Entity:** OrderItem
**Input:** OrderItem entity in DRAFT state
**Process:**
```
1. Validate pet is still available
2. Recalculate total_price
3. Set updated_at timestamp
4. Update order total amount
```
**Output:** OrderItem entity in CONFIRMED state
**Transition:** Update parent Order -> OrderPlacementProcessor

### OrderItemCancellationProcessor
**Entity:** OrderItem
**Input:** OrderItem entity in DRAFT state
**Process:**
```
1. Remove item from order
2. Recalculate order total
3. Set updated_at timestamp
4. Log cancellation event
```
**Output:** OrderItem entity in CANCELLED state
**Transition:** Update parent Order -> OrderPlacementProcessor
