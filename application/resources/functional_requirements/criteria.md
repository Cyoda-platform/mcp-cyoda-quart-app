# Criteria for Purrfect Pets API

## Pet Criteria

### PetAvailabilityCriterion
**Entity:** Pet
**Purpose:** Check if pet is available for reservation or sale
**Logic:** Verify pet state is AVAILABLE and not already reserved

**Pseudocode:**
```
evaluate(pet):
    if pet.meta.state == AVAILABLE:
        if pet.ownerId is null:
            return true
    return false
```

### PetSaleValidationCriterion
**Entity:** Pet
**Purpose:** Validate pet can be sold
**Logic:** Check pet is pending and owner is verified

**Pseudocode:**
```
evaluate(pet, owner):
    if pet.meta.state == PENDING:
        if owner.meta.state == ACTIVE:
            if pet.ownerId == owner.id:
                return true
    return false
```

## Owner Criteria

### OwnerVerificationCriterion
**Entity:** Owner
**Purpose:** Check if owner can be verified
**Logic:** Validate email verification and required information

**Pseudocode:**
```
evaluate(owner, verificationToken):
    if owner.meta.state == PENDING_VERIFICATION:
        if verificationToken is valid and not expired:
            if owner.email is verified:
                return true
    return false
```

### OwnerActivationCriterion
**Entity:** Owner
**Purpose:** Check if owner can be reactivated
**Logic:** Verify owner is inactive and account is in good standing

**Pseudocode:**
```
evaluate(owner):
    if owner.meta.state == INACTIVE:
        if owner has no outstanding issues:
            if owner account is in good standing:
                return true
    return false
```

### OwnerSuspensionCriterion
**Entity:** Owner
**Purpose:** Check if owner should be suspended
**Logic:** Validate suspension criteria are met

**Pseudocode:**
```
evaluate(owner, suspensionReason):
    if owner.meta.state == ACTIVE:
        if suspensionReason is valid:
            if suspension is justified:
                return true
    return false
```

### OwnerReinstateCriterion
**Entity:** Owner
**Purpose:** Check if suspended owner can be reinstated
**Logic:** Verify suspension period and conditions

**Pseudocode:**
```
evaluate(owner):
    if owner.meta.state == SUSPENDED:
        if suspension period is complete:
            if reinstatement conditions are met:
                return true
    return false
```

## Order Criteria

### OrderValidationCriterion
**Entity:** Order
**Purpose:** Validate order can be confirmed
**Logic:** Check order details, payment, and pet availability

**Pseudocode:**
```
evaluate(order):
    if order.meta.state == PLACED:
        if order.totalAmount > 0:
            if pet is still available:
                if owner is active:
                    if payment method is valid:
                        return true
    return false
```

### OrderShippingCriterion
**Entity:** Order
**Purpose:** Check if order is ready for shipping
**Logic:** Validate preparation is complete and shipping details

**Pseudocode:**
```
evaluate(order):
    if order.meta.state == PREPARING:
        if pet documentation is complete:
            if delivery address is valid:
                if shipping method is available:
                    return true
    return false
```

### OrderCancellationCriterion
**Entity:** Order
**Purpose:** Check if order can be cancelled
**Logic:** Validate cancellation is allowed based on order state

**Pseudocode:**
```
evaluate(order, cancellationReason):
    if order.meta.state in [PLACED, CONFIRMED]:
        if cancellationReason is provided:
            if cancellation policy allows:
                return true
    return false
```

### OrderReturnCriterion
**Entity:** Order
**Purpose:** Check if order can be returned
**Logic:** Validate return policy and conditions

**Pseudocode:**
```
evaluate(order, returnReason):
    if order.meta.state == DELIVERED:
        if return is within return period:
            if returnReason is valid:
                if pet is in returnable condition:
                    return true
    return false
```

## Category Criteria

### CategoryArchiveCriterion
**Entity:** Category
**Purpose:** Check if category can be archived
**Logic:** Ensure no active pets in category

**Pseudocode:**
```
evaluate(category):
    if category.meta.state == INACTIVE:
        if category has no active pets:
            if category has no pending orders:
                return true
    return false
```
