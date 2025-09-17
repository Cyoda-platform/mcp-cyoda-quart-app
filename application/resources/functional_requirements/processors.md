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

---

## Customer Processors

### CustomerRegistrationProcessor
**Entity:** Customer
**Input Data:** Customer entity with registration information
**Description:** Registers a new customer and activates their account
**Output:** Customer entity with state set to ACTIVE
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(customer):
    validate customer data (email, name, contact info required)
    check email uniqueness
    validate date of birth (must be 18+ for adoption)
    validate phone number format
    set registration date to current timestamp
    generate unique customer ID
    log customer registration
    return updated customer entity
```

### CustomerSuspensionProcessor
**Entity:** Customer
**Input Data:** Customer entity, suspension reason, suspension duration
**Description:** Suspends a customer account due to policy violations
**Output:** Customer entity with state set to SUSPENDED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(customer, suspensionReason, suspensionDuration):
    validate customer is currently active
    create suspension record with reason and duration
    cancel any pending adoption applications
    notify customer of suspension
    log suspension activity
    return updated customer entity
```

### CustomerReactivationProcessor
**Entity:** Customer
**Input Data:** Customer entity, reactivation notes
**Description:** Reactivates a suspended customer account
**Output:** Customer entity with state set to ACTIVE
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(customer, reactivationNotes):
    validate customer is currently suspended
    validate suspension issues have been resolved
    update suspension record with reactivation date
    notify customer of reactivation
    log reactivation activity
    return updated customer entity
```

### CustomerBlacklistProcessor
**Entity:** Customer
**Input Data:** Customer entity, blacklist reason
**Description:** Blacklists a customer permanently
**Output:** Customer entity with state set to BLACKLISTED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(customer, blacklistReason):
    validate customer is currently active or suspended
    create blacklist record with reason
    cancel all pending adoption applications
    revoke any current adoptions if necessary
    notify relevant staff
    log blacklist activity
    return updated customer entity
```

---

## AdoptionApplication Processors

### ApplicationSubmissionProcessor
**Entity:** AdoptionApplication
**Input Data:** AdoptionApplication entity with customer and pet information
**Description:** Processes a new adoption application submission
**Output:** AdoptionApplication entity with state set to SUBMITTED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(application):
    validate customer exists and is active
    validate pet exists and is available
    validate store exists and is active
    validate required application fields are complete
    set application date to current timestamp
    generate unique application ID
    notify store staff of new application
    log application submission
    return updated application entity
```

### ApplicationReviewStartProcessor
**Entity:** AdoptionApplication
**Input Data:** AdoptionApplication entity, reviewer information
**Description:** Starts the review process for a submitted application
**Output:** AdoptionApplication entity with state set to UNDER_REVIEW
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(application, reviewerInfo):
    validate application is currently submitted
    assign reviewer to application
    set review start date to current timestamp
    create review tracking record
    notify customer that review has started
    log review start activity
    return updated application entity
```

### ApplicationApprovalProcessor
**Entity:** AdoptionApplication
**Input Data:** AdoptionApplication entity, approval notes, reviewer
**Description:** Approves an adoption application after successful review
**Output:** AdoptionApplication entity with state set to APPROVED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(application, approvalNotes, reviewer):
    validate application is currently under review
    validate all approval criteria are met
    set approval date to current timestamp
    record approval notes and reviewer
    notify customer of approval
    create pet reservation for customer
    log approval activity
    return updated application entity
```

### ApplicationRejectionProcessor
**Entity:** AdoptionApplication
**Input Data:** AdoptionApplication entity, rejection reason, reviewer
**Description:** Rejects an adoption application after review
**Output:** AdoptionApplication entity with state set to REJECTED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(application, rejectionReason, reviewer):
    validate application is currently under review
    set rejection date to current timestamp
    record rejection reason and reviewer
    notify customer of rejection with reason
    log rejection activity
    return updated application entity
```

### ApplicationExpirationProcessor
**Entity:** AdoptionApplication
**Input Data:** AdoptionApplication entity
**Description:** Expires an application that has been pending too long
**Output:** AdoptionApplication entity with state set to EXPIRED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(application):
    validate application is submitted or under review
    check if application has exceeded time limit
    set expiration date to current timestamp
    notify customer of expiration
    log expiration activity
    return updated application entity
```

---

## Adoption Processors

### AdoptionCompletionProcessor
**Entity:** Adoption
**Input Data:** Adoption entity with completion details
**Description:** Completes the adoption process and records all details
**Output:** Adoption entity with state set to COMPLETED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(adoption):
    validate all adoption requirements are met
    validate adoption fee has been paid
    validate contract has been signed
    set adoption date to current timestamp
    record all adoption details
    update pet status to adopted
    notify customer of successful adoption
    log adoption completion
    return updated adoption entity
```

### FollowUpSchedulingProcessor
**Entity:** Adoption
**Input Data:** Adoption entity, follow-up date
**Description:** Schedules a follow-up for a completed adoption
**Output:** Adoption entity with state set to FOLLOW_UP_PENDING
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(adoption, followUpDate):
    validate adoption is currently completed
    set follow-up date
    create follow-up reminder
    notify staff of scheduled follow-up
    log follow-up scheduling
    return updated adoption entity
```

### FollowUpCompletionProcessor
**Entity:** Adoption
**Input Data:** Adoption entity, follow-up notes
**Description:** Completes the follow-up process for an adoption
**Output:** Adoption entity with state set to FOLLOW_UP_COMPLETED
**Transition:** null (state change handled by workflow)

**Pseudocode:**
```
process(adoption, followUpNotes):
    validate adoption has pending follow-up
    record follow-up completion date
    record follow-up notes
    mark follow-up as completed
    log follow-up completion
    return updated adoption entity
```

### AdoptionReturnProcessor
**Entity:** Adoption
**Input Data:** Adoption entity, return reason, return date
**Description:** Processes the return of an adopted pet
**Output:** Adoption entity with state set to RETURNED
**Transition:** Update related Pet entity with ADOPTED→AVAILABLE transition

**Pseudocode:**
```
process(adoption, returnReason, returnDate):
    validate adoption exists and is not already returned
    set return date and reason
    update pet status back to available
    trigger pet workflow transition
    calculate any refund amounts
    log return activity
    return updated adoption entity
```
