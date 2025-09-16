# Processors for Purrfect Pets API

## Pet Processors

### PetInitializationProcessor
**Entity:** Pet
**Input:** Pet entity with basic information
**Process:**
1. Validate pet data (name, category_id, price)
2. Set default values for optional fields
3. Generate unique pet ID
4. Set created_at timestamp
5. Initialize photo_urls as empty list if not provided
6. Set initial availability status
**Output:** Pet entity ready for availability

### PetReservationProcessor
**Entity:** Pet
**Input:** Pet entity and reservation details
**Process:**
1. Check if pet is currently available
2. Create reservation record with timestamp
3. Set reservation expiry time (24 hours)
4. Update pet status to pending
5. Send notification to customer
**Output:** Pet entity in pending state

### PetReleaseProcessor
**Entity:** Pet
**Input:** Pet entity in pending state
**Process:**
1. Remove reservation record
2. Clear reservation expiry time
3. Update pet status back to available
4. Send notification about release
**Output:** Pet entity back to available state

### PetSaleProcessor
**Entity:** Pet
**Input:** Pet entity and sale transaction details
**Process:**
1. Validate payment completion
2. Update pet ownership information
3. Generate sale receipt
4. Update inventory count
5. Send confirmation to buyer
6. Update pet status to sold
**Output:** Pet entity in sold state

### PetUnavailableProcessor
**Entity:** Pet
**Input:** Pet entity and unavailability reason
**Process:**
1. Record unavailability reason
2. Set unavailable timestamp
3. Update pet status to unavailable
4. Notify interested customers
**Output:** Pet entity in unavailable state

### PetAvailableProcessor
**Entity:** Pet
**Input:** Pet entity in unavailable state
**Process:**
1. Clear unavailability reason
2. Update availability timestamp
3. Update pet status to available
4. Notify interested customers
**Output:** Pet entity back to available state

### PetReturnProcessor
**Entity:** Pet
**Input:** Pet entity and return details
**Process:**
1. Validate return conditions
2. Process refund if applicable
3. Reset pet ownership
4. Update pet condition notes
5. Update pet status to available
**Output:** Pet entity back to available state

## Category Processors

### CategoryActivationProcessor
**Entity:** Category
**Input:** Category entity
**Process:**
1. Validate category name uniqueness
2. Set activation timestamp
3. Update category status to active
4. Enable category for pet assignments
**Output:** Category entity in active state

### CategoryDeactivationProcessor
**Entity:** Category
**Input:** Category entity
**Process:**
1. Check if category has active pets
2. Set deactivation timestamp
3. Update category status to inactive
4. Prevent new pet assignments
**Output:** Category entity in inactive state

## User Processors

### UserActivationProcessor
**Entity:** User
**Input:** User entity
**Process:**
1. Validate user email uniqueness
2. Hash password if not already hashed
3. Set activation timestamp
4. Send welcome email
5. Update user status to active
**Output:** User entity in active state

### UserDeactivationProcessor
**Entity:** User
**Input:** User entity
**Process:**
1. Set deactivation timestamp
2. Invalidate user sessions
3. Update user status to inactive
4. Send deactivation notification
**Output:** User entity in inactive state

### UserSuspensionProcessor
**Entity:** User
**Input:** User entity and suspension reason
**Process:**
1. Record suspension reason
2. Set suspension timestamp
3. Invalidate user sessions
4. Update user status to suspended
5. Send suspension notification
**Output:** User entity in suspended state

## Order Processors

### OrderPlacementProcessor
**Entity:** Order
**Input:** Order entity with items
**Process:**
1. Validate order items availability
2. Calculate total amount
3. Reserve pets in order
4. Set order timestamp
5. Generate order number
6. Update order status to placed
**Output:** Order entity in placed state
**Other Entity Updates:** Pet entities (transition to pending state)

### OrderApprovalProcessor
**Entity:** Order
**Input:** Order entity
**Process:**
1. Verify payment method
2. Confirm pet availability
3. Set approval timestamp
4. Update order status to approved
5. Send approval notification
**Output:** Order entity in approved state

### OrderShippingProcessor
**Entity:** Order
**Input:** Order entity and shipping details
**Process:**
1. Generate shipping label
2. Update shipping address if needed
3. Set ship_date
4. Update order status to shipped
5. Send tracking information
**Output:** Order entity in shipped state

### OrderDeliveryProcessor
**Entity:** Order
**Input:** Order entity and delivery confirmation
**Process:**
1. Record delivery timestamp
2. Update order status to delivered
3. Send delivery confirmation
4. Request customer feedback
**Output:** Order entity in delivered state

### OrderCancellationProcessor
**Entity:** Order
**Input:** Order entity and cancellation reason
**Process:**
1. Record cancellation reason
2. Process refund if payment made
3. Release reserved pets
4. Update order status to cancelled
5. Send cancellation notification
**Output:** Order entity in cancelled state
**Other Entity Updates:** Pet entities (transition back to available state)

## OrderItem Processors

### OrderItemInitializationProcessor
**Entity:** OrderItem
**Input:** OrderItem entity
**Process:**
1. Validate pet availability
2. Set unit_price from current pet price
3. Calculate total_price (quantity * unit_price)
4. Set creation timestamp
5. Update status to pending
**Output:** OrderItem entity in pending state

### OrderItemConfirmationProcessor
**Entity:** OrderItem
**Input:** OrderItem entity
**Process:**
1. Confirm pet is still available
2. Lock pet for this order
3. Update status to confirmed
4. Set confirmation timestamp
**Output:** OrderItem entity in confirmed state

### OrderItemShippingProcessor
**Entity:** OrderItem
**Input:** OrderItem entity
**Process:**
1. Prepare item for shipping
2. Update pet ownership
3. Update status to shipped
4. Set shipping timestamp
**Output:** OrderItem entity in shipped state
