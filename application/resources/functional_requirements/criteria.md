# Criteria for Purrfect Pets API

## Pet Criteria

### PetAvailabilityCriterion
**Entity:** Pet
**Purpose:** Check if pet is available for reservation
**Logic:**
- Pet state must be AVAILABLE
- Pet must not have any active reservations
- Pet must not be on medical hold
- Pet must have completed intake process

### MedicalClearanceCriterion
**Entity:** Pet
**Purpose:** Validate pet is medically cleared for adoption
**Logic:**
- All required vaccinations must be up to date
- Recent health examination must be completed
- No active medical conditions requiring treatment
- Veterinarian clearance must be documented

### AdoptionApprovalCriterion
**Entity:** Pet + AdoptionApplication
**Purpose:** Validate adoption can proceed
**Logic:**
- Pet must be in RESERVED state
- Adoption application must be APPROVED
- Customer must be in APPROVED state
- All adoption fees must be paid
- Adoption paperwork must be completed

## Customer Criteria

### CustomerDataValidationCriterion
**Entity:** Customer
**Purpose:** Validate customer data for verification
**Logic:**
- All required fields must be completed
- Email format must be valid
- Phone number format must be valid
- Address must be verifiable
- Age must be 18 or older

### CustomerEligibilityCriterion
**Entity:** Customer
**Purpose:** Check customer eligibility for pet adoption
**Logic:**
- Customer must be verified
- No history of animal abuse or neglect
- Suitable living conditions for pets
- Financial capability to care for pets
- No outstanding issues with previous adoptions

### SuspensionReviewCriterion
**Entity:** Customer
**Purpose:** Evaluate if customer suspension can be lifted
**Logic:**
- Suspension reason has been addressed
- Required waiting period has passed
- Customer has completed any required actions
- No new violations during suspension period

## AdoptionApplication Criteria

### ApplicationCompletenessCriterion
**Entity:** AdoptionApplication
**Purpose:** Validate application is complete for review
**Logic:**
- All required fields are filled
- Required documents are uploaded
- Application fee is paid
- Customer is in VERIFIED or APPROVED state
- Pet is available for adoption

### ApplicationApprovalCriterion
**Entity:** AdoptionApplication
**Purpose:** Determine if application should be approved
**Logic:**
- Customer background check passed
- References have been verified
- Home visit completed (if required)
- Customer meets pet-specific requirements
- No red flags in application review
- Customer financial capability verified

## Staff Criteria

### SuspensionReviewCriterion
**Entity:** Staff
**Purpose:** Evaluate if staff suspension can be lifted
**Logic:**
- Suspension investigation is complete
- Required corrective actions are completed
- No additional violations during suspension
- Management approval for reinstatement
- Required training completed if applicable
