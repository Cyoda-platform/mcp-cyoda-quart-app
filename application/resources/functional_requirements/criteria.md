# Criteria for Purrfect Pets API

## Pet Criteria

### PetPaymentCriterion
**Entity:** Pet
**Purpose:** Check if payment has been completed for pet purchase
**Logic:**
1. Verify payment transaction exists
2. Check payment status is completed
3. Validate payment amount matches pet price
4. Confirm payment method is valid
**Returns:** True if payment is completed successfully, False otherwise

## User Criteria

### UserReinstateableCriterion
**Entity:** User
**Purpose:** Check if suspended user can be reinstated
**Logic:**
1. Verify suspension reason allows reinstatement
2. Check if suspension period has been served
3. Validate no pending violations exist
4. Confirm user has completed required actions (if any)
**Returns:** True if user can be reinstated, False otherwise

## Order Criteria

### OrderValidationCriterion
**Entity:** Order
**Purpose:** Validate order before approval
**Logic:**
1. Check all order items are valid
2. Verify all pets in order are available
3. Validate shipping address is complete
4. Confirm payment method is provided
5. Check user account is active
6. Validate total amount calculation is correct
**Returns:** True if order is valid for approval, False otherwise

## OrderItem Criteria

### OrderItemValidationCriterion
**Entity:** OrderItem
**Purpose:** Validate order item before confirmation
**Logic:**
1. Check pet still exists and is available
2. Verify quantity is valid (positive integer)
3. Validate unit_price matches current pet price
4. Confirm total_price calculation is correct
5. Check pet is not already sold
**Returns:** True if order item is valid for confirmation, False otherwise
