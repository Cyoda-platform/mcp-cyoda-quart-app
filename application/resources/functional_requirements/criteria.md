# Criteria for Purrfect Pets API

## Pet Criteria

### PetValidationCriterion
**Entity:** Pet
**Purpose:** Validate pet data before making it available
**Conditions:**
```
1. Name is not null and not empty
2. Category ID is not null and category exists
3. Category is in ACTIVE state
4. Price is greater than or equal to 0
5. Age is greater than 0 if provided
6. Weight is greater than 0 if provided
7. Photo URLs are valid URLs if provided
```
**Result:** true if all conditions are met, false otherwise

### PetRestoreCriterion
**Entity:** Pet
**Purpose:** Check if pet can be restored to available status
**Conditions:**
```
1. Pet is currently in UNAVAILABLE state
2. Pet has no pending orders
3. Pet data is still valid (category exists and is active)
4. No system flags preventing restoration
```
**Result:** true if pet can be restored, false otherwise

## Category Criteria

### CategoryValidationCriterion
**Entity:** Category
**Purpose:** Validate category before activation
**Conditions:**
```
1. Name is not null and not empty
2. Name is unique across all categories
3. Name length is between 2 and 50 characters
4. Description length is less than 500 characters if provided
```
**Result:** true if all conditions are met, false otherwise

## Customer Criteria

### CustomerVerificationCriterion
**Entity:** Customer
**Purpose:** Check if customer can be verified and activated
**Conditions:**
```
1. Email verification is completed
2. Username is unique
3. Email is unique
4. All required fields are provided
5. Email format is valid
6. Phone format is valid if provided
```
**Result:** true if customer can be activated, false otherwise

### CustomerReactivationCriterion
**Entity:** Customer
**Purpose:** Check if suspended customer can be reactivated
**Conditions:**
```
1. Customer is currently in SUSPENDED state
2. Suspension reason allows reactivation
3. No outstanding issues or violations
4. Account information is still valid
5. Email is still verified
```
**Result:** true if customer can be reactivated, false otherwise

## Order Criteria

### OrderValidationCriterion
**Entity:** Order
**Purpose:** Validate order before placement
**Conditions:**
```
1. Customer exists and is in ACTIVE state
2. Order has at least one order item
3. All order items are valid
4. All pets in order items are available
5. Total amount is greater than 0
6. Shipping address is provided and valid
7. Customer has no suspended orders
```
**Result:** true if order can be placed, false otherwise

### OrderApprovalCriterion
**Entity:** Order
**Purpose:** Check if order can be approved for processing
**Conditions:**
```
1. Order is in PLACED state
2. Payment information is valid
3. All pets are still available
4. Customer account is still active
5. Inventory is sufficient
6. No fraud flags detected
```
**Result:** true if order can be approved, false otherwise

## OrderItem Criteria

### OrderItemValidationCriterion
**Entity:** OrderItem
**Purpose:** Validate order item before confirmation
**Conditions:**
```
1. Pet exists and is available
2. Quantity is greater than 0
3. Unit price matches current pet price
4. Pet is not already in another pending order
5. Order exists and is in valid state
```
**Result:** true if order item can be confirmed, false otherwise

## General Validation Rules

### Common Validation Patterns
```
1. String fields: Check for null, empty, and length constraints
2. Numeric fields: Check for positive values where applicable
3. Email format: Use standard email regex validation
4. Phone format: Accept various international formats
5. URL validation: Check for valid URL format in photo_urls
6. Foreign key validation: Ensure referenced entities exist
7. State validation: Ensure referenced entities are in valid states
8. Uniqueness validation: Check for duplicate values where required
```

### Error Handling
```
1. Return false for any validation failure
2. Log validation failures for debugging
3. Provide meaningful error messages
4. Handle null pointer exceptions gracefully
5. Validate all conditions before returning result
```

### Performance Considerations
```
1. Cache frequently accessed reference data
2. Minimize database queries in criteria
3. Use efficient validation algorithms
4. Avoid complex calculations in criteria
5. Keep criteria logic simple and fast
```
