# Purrfect Pets - Processor Requirements

## Overview
This document defines the processors for business logic in the Purrfect Pets API application. Each processor implements the business logic for specific workflow transitions.

## Pet Processors

### 1. PetCreationProcessor
**Entity**: Pet  
**Input**: New pet data  
**Purpose**: Initialize a new pet record and set up basic information  
**Output**: Pet entity with DRAFT state  
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(pet):
    validate required fields (name, photoUrls)
    set default values for optional fields
    generate unique pet ID
    set createdAt and updatedAt timestamps
    set initial price if not provided
    return updated pet entity
```

### 2. PetValidationProcessor
**Entity**: Pet  
**Input**: Pet in DRAFT state  
**Purpose**: Validate pet information is complete and ready for availability  
**Output**: Pet entity with AVAILABLE state  
**Transition**: DRAFT → AVAILABLE

**Pseudocode**:
```
process(pet):
    validate all required fields are present
    validate price is positive
    validate age is reasonable (0-300 months)
    validate weight is positive if provided
    validate photo URLs are accessible
    validate category exists and is active
    validate all tags exist and are active
    set updatedAt timestamp
    return updated pet entity
```

### 3. PetReservationProcessor
**Entity**: Pet  
**Input**: Pet in AVAILABLE state with order information  
**Purpose**: Reserve pet for a pending order  
**Output**: Pet entity with PENDING state  
**Transition**: AVAILABLE → PENDING

**Pseudocode**:
```
process(pet, orderData):
    validate order information is complete
    validate user exists and is active
    create new order entity with PLACED state
    trigger order workflow transition to CONFIRMED
    set pet updatedAt timestamp
    return updated pet entity
```

### 4. PetSaleProcessor
**Entity**: Pet  
**Input**: Pet in PENDING state with payment confirmation  
**Purpose**: Complete the sale of a pet  
**Output**: Pet entity with SOLD state  
**Transition**: PENDING → SOLD

**Pseudocode**:
```
process(pet, paymentData):
    validate payment is completed
    update associated order to PROCESSING state
    trigger order workflow transition to PROCESSING
    set pet sale date
    set pet updatedAt timestamp
    send confirmation email to customer
    return updated pet entity
```

### 5. PetReleaseProcessor
**Entity**: Pet  
**Input**: Pet in PENDING state  
**Purpose**: Release pet from pending status back to available  
**Output**: Pet entity with AVAILABLE state  
**Transition**: PENDING → AVAILABLE

**Pseudocode**:
```
process(pet):
    find associated pending order
    cancel the order (trigger order workflow to CANCELLED)
    clear any reservation data
    set pet updatedAt timestamp
    return updated pet entity
```

### 6. PetReactivationProcessor
**Entity**: Pet  
**Input**: Pet in UNAVAILABLE state  
**Purpose**: Reactivate an unavailable pet  
**Output**: Pet entity with AVAILABLE state  
**Transition**: UNAVAILABLE → AVAILABLE

**Pseudocode**:
```
process(pet):
    validate pet health information is current
    validate pet is still in good condition
    update any changed information
    set pet updatedAt timestamp
    return updated pet entity
```

### 7. PetArchiveProcessor
**Entity**: Pet  
**Input**: Pet in SOLD state  
**Purpose**: Archive a sold pet record  
**Output**: Pet entity with ARCHIVED state  
**Transition**: SOLD → ARCHIVED

**Pseudocode**:
```
process(pet):
    validate pet has been sold for sufficient time
    validate all associated orders are completed
    set archive date
    set pet updatedAt timestamp
    return updated pet entity
```

## Category Processors

### 1. CategoryCreationProcessor
**Entity**: Category  
**Input**: New category data  
**Purpose**: Initialize a new category record  
**Output**: Category entity with ACTIVE state  
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(category):
    validate required fields (name)
    check for duplicate category names
    generate unique category ID
    set createdAt and updatedAt timestamps
    set default description if not provided
    return updated category entity
```

### 2. CategoryReactivationProcessor
**Entity**: Category  
**Input**: Category in INACTIVE state  
**Purpose**: Reactivate an inactive category  
**Output**: Category entity with ACTIVE state  
**Transition**: INACTIVE → ACTIVE

**Pseudocode**:
```
process(category):
    validate category information is still relevant
    set updatedAt timestamp
    return updated category entity
```

### 3. CategoryArchiveProcessor
**Entity**: Category  
**Input**: Category in INACTIVE state  
**Purpose**: Archive a category that is no longer needed  
**Output**: Category entity with ARCHIVED state  
**Transition**: INACTIVE → ARCHIVED

**Pseudocode**:
```
process(category):
    validate no pets are currently using this category
    set archive date
    set updatedAt timestamp
    return updated category entity
```

## Tag Processors

### 1. TagCreationProcessor
**Entity**: Tag  
**Input**: New tag data  
**Purpose**: Initialize a new tag record  
**Output**: Tag entity with ACTIVE state  
**Transition**: null (automatic state change)

**Pseudocode**:
```
process(tag):
    validate required fields (name)
    check for duplicate tag names
    generate unique tag ID
    set createdAt timestamp
    set default color if not provided
    return updated tag entity
```

### 2. TagArchiveProcessor
**Entity**: Tag  
**Input**: Tag in INACTIVE state  
**Purpose**: Archive a tag that is no longer used  
**Output**: Tag entity with ARCHIVED state  
**Transition**: INACTIVE → ARCHIVED

**Pseudocode**:
```
process(tag):
    validate no pets are currently using this tag
    set archive date
    return updated tag entity
```
