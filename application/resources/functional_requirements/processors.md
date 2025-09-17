# Processors for Purrfect Pets API

## Pet Processors

### PetIntakeProcessor
**Entity:** Pet
**Input Data:** Pet entity with basic information (name, category, breed, age, etc.)
**Description:** Processes a new pet entering the system, validates data, assigns ID, sets arrival date
**Output:** Pet entity with state set to AVAILABLE, arrival date populated
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(pet):
    validate pet data (name, category, breed required)
    set arrival date to current timestamp
    validate age is positive
    validate weight is positive if provided
    set default values for boolean fields if not provided
    generate unique ID
    save pet to database
    return updated pet entity
```

### PetReservationProcessor
**Entity:** Pet
**Input Data:** Pet entity, customer ID, adoption application ID
**Description:** Reserves a pet for an approved adoption application
**Output:** Pet entity with state set to RESERVED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(pet, customerId, applicationId):
    validate customer exists and is active
    validate adoption application exists and is approved
    validate pet is currently available
    create reservation record linking pet, customer, and application
    log reservation activity
    return updated pet entity
```

### PetAdoptionProcessor
**Entity:** Pet
**Input Data:** Pet entity, adoption details (fee, contract info, etc.)
**Description:** Completes the adoption process for a reserved pet
**Output:** Pet entity with state set to ADOPTED, creates Adoption entity
**Transition:** Create new Adoption entity with INITIAL→COMPLETED transition

**Pseudocode:**
```
process(pet, adoptionDetails):
    validate pet is currently reserved
    validate all adoption requirements are met (contract signed, fee paid)
    set adoption date to current timestamp
    create adoption record with all details
    update pet with adoption information
    trigger adoption workflow for new adoption entity
    return updated pet entity
```

### PetReservationCancellationProcessor
**Entity:** Pet
**Input Data:** Pet entity, cancellation reason
**Description:** Cancels a pet reservation and makes pet available again
**Output:** Pet entity with state set to AVAILABLE
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(pet, cancellationReason):
    validate pet is currently reserved
    remove reservation record
    log cancellation with reason
    clear reservation-related fields
    return updated pet entity
```

### PetMedicalHoldProcessor
**Entity:** Pet
**Input Data:** Pet entity, medical notes, expected duration
**Description:** Places pet on medical hold for health issues
**Output:** Pet entity with state set to MEDICAL_HOLD
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(pet, medicalNotes, expectedDuration):
    validate pet is not already adopted
    create medical hold record with notes and expected duration
    log medical hold activity
    notify relevant staff
    return updated pet entity
```

### PetMedicalClearanceProcessor
**Entity:** Pet
**Input Data:** Pet entity, clearance notes, veterinarian approval
**Description:** Clears pet from medical hold after treatment
**Output:** Pet entity with state set to AVAILABLE
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(pet, clearanceNotes, vetApproval):
    validate pet is currently on medical hold
    validate veterinarian approval is provided
    update medical hold record with clearance information
    log medical clearance activity
    return updated pet entity
```

### PetReturnProcessor
**Entity:** Pet
**Input Data:** Pet entity, return reason, return date
**Description:** Processes the return of an adopted pet
**Output:** Pet entity with state set to AVAILABLE, updates Adoption entity
**Transition:** Update related Adoption entity with COMPLETED→RETURNED transition

**Pseudocode:**
```
process(pet, returnReason, returnDate):
    validate pet is currently adopted
    find related adoption record
    update adoption record with return information
    trigger adoption return workflow
    reset pet adoption-related fields
    log return activity
    return updated pet entity
```

---

## Store Processors

### StoreActivationProcessor
**Entity:** Store
**Input Data:** Store entity with basic information
**Description:** Activates a new store and makes it operational
**Output:** Store entity with state set to ACTIVE
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(store):
    validate store data (name, address, contact info required)
    validate opening hours format
    set current pet count to 0
    validate capacity is positive
    generate unique store ID
    log store activation
    return updated store entity
```

### StoreTemporaryClosureProcessor
**Entity:** Store
**Input Data:** Store entity, closure reason, expected reopening date
**Description:** Temporarily closes a store
**Output:** Store entity with state set to TEMPORARILY_CLOSED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(store, closureReason, expectedReopeningDate):
    validate store is currently active
    create closure record with reason and expected reopening
    notify customers with pending applications
    log temporary closure
    return updated store entity
```

### StoreReopeningProcessor
**Entity:** Store
**Input Data:** Store entity, reopening notes
**Description:** Reopens a temporarily closed store
**Output:** Store entity with state set to ACTIVE
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(store, reopeningNotes):
    validate store is temporarily closed
    update closure record with actual reopening date
    notify relevant stakeholders
    log store reopening
    return updated store entity
```

### StorePermanentClosureProcessor
**Entity:** Store
**Input Data:** Store entity, closure reason, closure date
**Description:** Permanently closes a store
**Output:** Store entity with state set to PERMANENTLY_CLOSED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(store, closureReason, closureDate):
    validate store is currently active or temporarily closed
    transfer all pets to other stores
    cancel all pending adoption applications
    create permanent closure record
    log permanent closure
    return updated store entity
```
