# Criteria for Purrfect Pets API

## Pet Criteria

### PetAvailabilityCriterion
**Entity:** Pet
**Description:** Checks if a pet is available for reservation
**Logic:** Validates that the pet's current state is AVAILABLE and not already reserved

**Pseudocode:**
```
evaluate(pet):
    if pet.meta.state != AVAILABLE:
        return false, "Pet is not available for reservation"
    
    if pet has active reservation:
        return false, "Pet is already reserved"
    
    return true, "Pet is available for reservation"
```

### AdoptionReadinessCriterion
**Entity:** Pet
**Description:** Checks if a pet is ready for adoption completion
**Logic:** Validates that all adoption requirements are met

**Pseudocode:**
```
evaluate(pet, adoptionDetails):
    if pet.meta.state != RESERVED:
        return false, "Pet must be reserved before adoption"
    
    if not adoptionDetails.contractSigned:
        return false, "Adoption contract must be signed"
    
    if not adoptionDetails.feeReceived:
        return false, "Adoption fee must be received"
    
    if pet.vaccinated == false:
        return false, "Pet must be vaccinated before adoption"
    
    return true, "Pet is ready for adoption"
```

### MedicalClearanceCriterion
**Entity:** Pet
**Description:** Checks if a pet can be cleared from medical hold
**Logic:** Validates that medical treatment is complete and veterinarian approval is provided

**Pseudocode:**
```
evaluate(pet, clearanceData):
    if pet.meta.state != MEDICAL_HOLD:
        return false, "Pet is not on medical hold"
    
    if not clearanceData.veterinarianApproval:
        return false, "Veterinarian approval required for medical clearance"
    
    if clearanceData.treatmentComplete != true:
        return false, "Medical treatment must be completed"
    
    return true, "Pet is cleared for release from medical hold"
```

---

## Store Criteria

### StoreReopeningCriterion
**Entity:** Store
**Description:** Checks if a temporarily closed store can be reopened
**Logic:** Validates that closure issues have been resolved

**Pseudocode:**
```
evaluate(store, reopeningData):
    if store.meta.state != TEMPORARILY_CLOSED:
        return false, "Store is not temporarily closed"
    
    if not reopeningData.issuesResolved:
        return false, "Closure issues must be resolved before reopening"
    
    if not reopeningData.staffAvailable:
        return false, "Adequate staff must be available for reopening"
    
    if not reopeningData.facilitiesReady:
        return false, "Store facilities must be ready for operation"
    
    return true, "Store is ready for reopening"
```

---

## Customer Criteria

### CustomerReactivationCriterion
**Entity:** Customer
**Description:** Checks if a suspended customer account can be reactivated
**Logic:** Validates that suspension issues have been resolved

**Pseudocode:**
```
evaluate(customer, reactivationData):
    if customer.meta.state != SUSPENDED:
        return false, "Customer account is not suspended"
    
    if not reactivationData.issuesResolved:
        return false, "Suspension issues must be resolved"
    
    if reactivationData.hasOutstandingDebts:
        return false, "Customer must resolve outstanding debts"
    
    if not reactivationData.agreesToTerms:
        return false, "Customer must agree to updated terms"
    
    return true, "Customer account can be reactivated"
```

---

## AdoptionApplication Criteria

### ApplicationApprovalCriterion
**Entity:** AdoptionApplication
**Description:** Checks if an adoption application can be approved
**Logic:** Validates that all application requirements are met

**Pseudocode:**
```
evaluate(application, reviewData):
    if application.meta.state != UNDER_REVIEW:
        return false, "Application is not under review"
    
    if not reviewData.backgroundCheckPassed:
        return false, "Background check must pass"
    
    if not reviewData.referencesVerified:
        return false, "References must be verified"
    
    if not reviewData.housingApproved:
        return false, "Housing situation must be approved"
    
    if reviewData.customerBlacklisted:
        return false, "Customer is blacklisted"
    
    if not reviewData.petCompatibilityConfirmed:
        return false, "Pet compatibility must be confirmed"
    
    return true, "Application can be approved"
```
