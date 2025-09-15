# Purrfect Pets API - Criteria Requirements

## Overview
This document defines the criteria for conditional logic in the Purrfect Pets API system. Criteria are used to validate conditions before allowing transitions.

## Pet Criteria

### PetAvailabilityCriterion
**Entity**: Pet  
**Purpose**: Validates that a pet is available for reservation  
**Used in**: Pet workflow transition from AVAILABLE to RESERVED

**Validation Logic**:
```
evaluate(pet, context):
    if pet.state != AVAILABLE:
        return false, "Pet is not available for reservation"
    
    if pet has active AdoptionApplication in APPROVED state:
        return false, "Pet already has an approved adoption application"
    
    if pet.medicalHoldReason is not null:
        return false, "Pet is on medical hold"
    
    return true, "Pet is available for reservation"
```

### PetHealthCriterion
**Entity**: Pet  
**Purpose**: Validates that a pet is healthy and cleared for adoption  
**Used in**: Pet workflow transition from MEDICAL_HOLD to AVAILABLE

**Validation Logic**:
```
evaluate(pet, context):
    if pet.medicalClearanceDate is null:
        return false, "Pet has not received medical clearance"
    
    if pet.vaccinated != true:
        return false, "Pet must be vaccinated before becoming available"
    
    if pet.medicalClearanceNotes is empty:
        return false, "Medical clearance notes are required"
    
    veterinaryCheckDate = pet.medicalClearanceDate
    if veterinaryCheckDate is older than 30 days:
        return false, "Medical clearance is expired (older than 30 days)"
    
    return true, "Pet is healthy and cleared for adoption"
```

## Owner Criteria

### OwnerInformationCriterion
**Entity**: Owner  
**Purpose**: Validates that owner has provided complete and valid information  
**Used in**: Owner workflow transition from REGISTERED to VERIFIED

**Validation Logic**:
```
evaluate(owner, context):
    if owner.firstName is empty or owner.lastName is empty:
        return false, "First name and last name are required"
    
    if owner.email is empty or not valid email format:
        return false, "Valid email address is required"
    
    if owner.phone is empty or not valid phone format:
        return false, "Valid phone number is required"
    
    if owner.address is empty:
        return false, "Address is required"
    
    if owner.city is empty or owner.state is empty or owner.zipCode is empty:
        return false, "Complete address (city, state, zip code) is required"
    
    if owner.dateOfBirth is null:
        return false, "Date of birth is required"
    
    age = calculate age from owner.dateOfBirth
    if age < 18:
        return false, "Owner must be at least 18 years old"
    
    if owner.housingType is empty:
        return false, "Housing type information is required"
    
    return true, "Owner information is complete and valid"
```

### OwnerBackgroundCheckCriterion
**Entity**: Owner  
**Purpose**: Validates that owner has passed background checks for pet adoption  
**Used in**: Owner workflow transition from VERIFIED to APPROVED

**Validation Logic**:
```
evaluate(owner, context):
    if owner.backgroundCheckStatus != "PASSED":
        return false, "Background check must be completed and passed"
    
    if owner.references is empty or owner.references.size() < 2:
        return false, "At least 2 references are required"
    
    for each reference in owner.references:
        if reference.contactVerified != true:
            return false, "All references must be verified"
    
    if owner.veterinarianContact is empty and owner.hasOtherPets == true:
        return false, "Veterinarian contact is required for owners with other pets"
    
    if owner.experienceLevel is empty:
        return false, "Pet experience level must be specified"
    
    return true, "Owner has passed all background checks"
```

## Order Criteria

### PaymentValidationCriterion
**Entity**: Order  
**Purpose**: Validates that payment for an order is successful  
**Used in**: Order workflow transition from PENDING to CONFIRMED

**Validation Logic**:
```
evaluate(order, context):
    if order.paymentMethod is empty:
        return false, "Payment method is required"
    
    if order.totalAmount <= 0:
        return false, "Order total must be greater than zero"
    
    paymentResult = validatePaymentWithGateway(order.paymentDetails)
    if paymentResult.status != "SUCCESS":
        return false, "Payment validation failed: " + paymentResult.errorMessage
    
    if paymentResult.amount != order.totalAmount:
        return false, "Payment amount does not match order total"
    
    for each orderItem in order.items:
        if orderItem.petId is not null:
            pet = getPetById(orderItem.petId)
            if pet.state != AVAILABLE and pet.state != RESERVED:
                return false, "Pet " + pet.name + " is no longer available"
    
    return true, "Payment is valid and successful"
```

## AdoptionApplication Criteria

### AdoptionApprovalCriterion
**Entity**: AdoptionApplication  
**Purpose**: Validates that adoption application meets approval requirements  
**Used in**: Pet workflow transition from RESERVED to ADOPTED

**Validation Logic**:
```
evaluate(adoptionApplication, context):
    if adoptionApplication.state != APPROVED:
        return false, "Adoption application must be approved"
    
    owner = getOwnerById(adoptionApplication.ownerId)
    if owner.state != APPROVED:
        return false, "Owner must be approved for adoptions"
    
    pet = getPetById(adoptionApplication.petId)
    if pet.state != RESERVED:
        return false, "Pet must be in reserved state"
    
    if adoptionApplication.agreedToTerms != true:
        return false, "Applicant must agree to terms and conditions"
    
    if adoptionApplication.reviewedBy is empty:
        return false, "Application must be reviewed by staff"
    
    daysSinceApproval = days between adoptionApplication.approvalDate and current date
    if daysSinceApproval > 30:
        return false, "Adoption approval has expired (older than 30 days)"
    
    return true, "Adoption application meets all approval requirements"
```

### AdoptionEligibilityCriterion
**Entity**: AdoptionApplication  
**Purpose**: Validates that applicant is eligible for pet adoption  
**Used in**: AdoptionApplication workflow transition from UNDER_REVIEW to APPROVED

**Validation Logic**:
```
evaluate(adoptionApplication, context):
    owner = getOwnerById(adoptionApplication.ownerId)
    pet = getPetById(adoptionApplication.petId)
    
    if owner.state != APPROVED:
        return false, "Owner must be approved before adoption"
    
    if pet.state != AVAILABLE and pet.state != RESERVED:
        return false, "Pet is not available for adoption"
    
    if adoptionApplication.reasonForAdoption is empty:
        return false, "Reason for adoption must be provided"
    
    if adoptionApplication.livingArrangement is empty:
        return false, "Living arrangement details must be provided"
    
    if adoptionApplication.workSchedule is empty:
        return false, "Work schedule information must be provided"
    
    if pet.category.name == "Dog" and owner.hasYard == false and owner.housingType == "apartment":
        if pet.size == "large":
            return false, "Large dogs require a yard or house"
    
    if owner.hasOtherPets == true and adoptionApplication.veterinarianContact is empty:
        return false, "Veterinarian contact required for owners with other pets"
    
    if adoptionApplication.references is empty or adoptionApplication.references.size() < 2:
        return false, "At least 2 references are required"
    
    for each reference in adoptionApplication.references:
        if reference.verified != true:
            return false, "All references must be verified"
    
    if owner.experienceLevel == "beginner" and pet.specialNeeds == true:
        return false, "Beginner owners cannot adopt pets with special needs"
    
    activeApplications = getActiveAdoptionApplicationsForOwner(owner.id)
    if activeApplications.size() > 3:
        return false, "Owner has too many active adoption applications"
    
    return true, "Applicant is eligible for pet adoption"
```

## General Validation Criteria

### EntityExistenceCriterion
**Purpose**: Generic criterion to validate that referenced entities exist  
**Used in**: Various workflows where entity relationships need validation

**Validation Logic**:
```
evaluate(entity, context):
    for each foreignKey in entity.foreignKeys:
        referencedEntity = getEntityById(foreignKey.entityType, foreignKey.id)
        if referencedEntity is null:
            return false, "Referenced " + foreignKey.entityType + " with ID " + foreignKey.id + " does not exist"
    
    return true, "All referenced entities exist"
```

### BusinessHoursCriterion
**Purpose**: Validates that operations are performed during business hours  
**Used in**: Manual transitions that require staff intervention

**Validation Logic**:
```
evaluate(entity, context):
    currentTime = getCurrentTime()
    currentDay = getCurrentDayOfWeek()
    
    if currentDay == SATURDAY or currentDay == SUNDAY:
        return false, "Operation not allowed on weekends"
    
    businessStartHour = 9  // 9 AM
    businessEndHour = 17   // 5 PM
    
    if currentTime.hour < businessStartHour or currentTime.hour >= businessEndHour:
        return false, "Operation only allowed during business hours (9 AM - 5 PM)"
    
    return true, "Operation is within business hours"
```

### DataIntegrityCriterion
**Purpose**: Validates data integrity constraints  
**Used in**: Various workflows to ensure data consistency

**Validation Logic**:
```
evaluate(entity, context):
    if entity.createdAt is null:
        return false, "Created timestamp is required"
    
    if entity.updatedAt is null:
        return false, "Updated timestamp is required"
    
    if entity.updatedAt < entity.createdAt:
        return false, "Updated timestamp cannot be before created timestamp"
    
    if entity.id is null or entity.id <= 0:
        return false, "Valid entity ID is required"
    
    return true, "Data integrity constraints are satisfied"
```
