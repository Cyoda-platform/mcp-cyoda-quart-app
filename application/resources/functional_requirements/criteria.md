# Criteria for Purrfect Pets API

## Pet Criteria

### PetAvailabilityCriterion

**Entity:** Pet
**Description:** Checks if a pet is available for reservation or sale
**Usage:** Used in transitions from available state to pending or sold states

**Validation Logic:**
- Pet status must be 'available'
- Pet must not have an active reservation
- Pet must not be marked as sold
- Pet must have valid category and required information

### PetSaleValidationCriterion

**Entity:** Pet
**Description:** Validates that a pet can be sold from pending state
**Usage:** Used in transition from pending to sold state

**Validation Logic:**
- Pet status must be 'pending'
- Pet must have an active reservation
- Reservation must not be expired
- Customer making the purchase must match the reservation holder
- Payment information must be valid and confirmed

## Order Criteria

### OrderValidationCriterion

**Entity:** Order
**Description:** Validates that an order can be approved
**Usage:** Used in transition from placed to approved state

**Validation Logic:**
- Order status must be 'placed'
- Associated pet must exist and be available/pending
- Customer information must be complete and valid
- Payment must be confirmed
- Delivery address must be valid
- Order amount must match pet price

### OrderDeliveryCriterion

**Entity:** Order
**Description:** Validates that an order can be marked as delivered
**Usage:** Used in transition from approved to delivered state

**Validation Logic:**
- Order status must be 'approved'
- Delivery date must be valid (not in future beyond reasonable limit)
- Delivery staff member must be valid
- Customer signature or confirmation must be provided
- Associated pet must be in 'sold' state

## User Criteria

### UserReactivationCriterion

**Entity:** User
**Description:** Checks if an inactive user can be reactivated
**Usage:** Used in transition from inactive to active state

**Validation Logic:**
- User status must be 'inactive'
- User must not have any outstanding violations
- User account must not be permanently banned
- Reactivation request must be within allowed timeframe (e.g., within 1 year)
- User must verify their identity (email verification)

### UserSuspensionCriterion

**Entity:** User
**Description:** Validates that a user can be suspended
**Usage:** Used in transition from active to suspended state

**Validation Logic:**
- User status must be 'active'
- Valid suspension reason must be provided
- Suspension must be authorized by admin user
- Suspension duration must be within policy limits
- User must not already have maximum number of suspensions

### UserUnsuspensionCriterion

**Entity:** User
**Description:** Checks if a suspended user can be unsuspended
**Usage:** Used in transition from suspended to active state

**Validation Logic:**
- User status must be 'suspended'
- Suspension period requirements must be met
- User must have completed any required actions (e.g., training, acknowledgment)
- Unsuspension must be authorized by admin user
- User must not have repeated violations that warrant permanent ban
