# Workflows for Purrfect Pets API

## Pet Workflow

**Name:** PetWorkflow

**States:**
- INITIAL (starting state)
- AVAILABLE (pet is available for adoption)
- RESERVED (pet is reserved for a customer)
- ADOPTED (pet has been adopted)
- MEDICAL_HOLD (pet is under medical care)
- UNAVAILABLE (pet is temporarily unavailable)

**Transitions:**

1. **INITIAL → AVAILABLE**
   - Type: Automatic
   - Processor: PetIntakeProcessor
   - Criterion: None
   - Description: Pet enters the system and becomes available

2. **AVAILABLE → RESERVED**
   - Type: Manual
   - Processor: PetReservationProcessor
   - Criterion: PetAvailabilityCriterion
   - Description: Pet is reserved for an approved adoption application

3. **RESERVED → ADOPTED**
   - Type: Manual
   - Processor: PetAdoptionProcessor
   - Criterion: AdoptionReadinessCriterion
   - Description: Pet adoption is completed

4. **RESERVED → AVAILABLE**
   - Type: Manual
   - Processor: PetReservationCancellationProcessor
   - Criterion: None
   - Description: Reservation is cancelled, pet becomes available again

5. **AVAILABLE → MEDICAL_HOLD**
   - Type: Manual
   - Processor: PetMedicalHoldProcessor
   - Criterion: None
   - Description: Pet needs medical attention

6. **MEDICAL_HOLD → AVAILABLE**
   - Type: Manual
   - Processor: PetMedicalClearanceProcessor
   - Criterion: MedicalClearanceCriterion
   - Description: Pet is cleared from medical hold

7. **ADOPTED → AVAILABLE**
   - Type: Manual
   - Processor: PetReturnProcessor
   - Criterion: None
   - Description: Pet is returned by adopter

8. **AVAILABLE → UNAVAILABLE**
   - Type: Manual
   - Processor: None
   - Criterion: None
   - Description: Pet becomes temporarily unavailable

9. **UNAVAILABLE → AVAILABLE**
   - Type: Manual
   - Processor: None
   - Criterion: None
   - Description: Pet becomes available again

```mermaid
stateDiagram-v2
    [*] --> INITIAL
    INITIAL --> AVAILABLE : PetIntakeProcessor
    AVAILABLE --> RESERVED : PetReservationProcessor / PetAvailabilityCriterion
    RESERVED --> ADOPTED : PetAdoptionProcessor / AdoptionReadinessCriterion
    RESERVED --> AVAILABLE : PetReservationCancellationProcessor
    AVAILABLE --> MEDICAL_HOLD : PetMedicalHoldProcessor
    MEDICAL_HOLD --> AVAILABLE : PetMedicalClearanceProcessor / MedicalClearanceCriterion
    ADOPTED --> AVAILABLE : PetReturnProcessor
    AVAILABLE --> UNAVAILABLE
    UNAVAILABLE --> AVAILABLE
```

---

## Store Workflow

**Name:** StoreWorkflow

**States:**
- INITIAL (starting state)
- ACTIVE (store is operational)
- TEMPORARILY_CLOSED (store is temporarily closed)
- PERMANENTLY_CLOSED (store is permanently closed)

**Transitions:**

1. **INITIAL → ACTIVE**
   - Type: Automatic
   - Processor: StoreActivationProcessor
   - Criterion: None
   - Description: Store is activated and becomes operational

2. **ACTIVE → TEMPORARILY_CLOSED**
   - Type: Manual
   - Processor: StoreTemporaryClosureProcessor
   - Criterion: None
   - Description: Store is temporarily closed

3. **TEMPORARILY_CLOSED → ACTIVE**
   - Type: Manual
   - Processor: StoreReopeningProcessor
   - Criterion: StoreReopeningCriterion
   - Description: Store reopens after temporary closure

4. **ACTIVE → PERMANENTLY_CLOSED**
   - Type: Manual
   - Processor: StorePermanentClosureProcessor
   - Criterion: None
   - Description: Store is permanently closed

```mermaid
stateDiagram-v2
    [*] --> INITIAL
    INITIAL --> ACTIVE : StoreActivationProcessor
    ACTIVE --> TEMPORARILY_CLOSED : StoreTemporaryClosureProcessor
    TEMPORARILY_CLOSED --> ACTIVE : StoreReopeningProcessor / StoreReopeningCriterion
    ACTIVE --> PERMANENTLY_CLOSED : StorePermanentClosureProcessor
```

---

## Customer Workflow

**Name:** CustomerWorkflow

**States:**
- INITIAL (starting state)
- ACTIVE (customer account is active)
- SUSPENDED (customer account is suspended)
- BLACKLISTED (customer is blacklisted)

**Transitions:**

1. **INITIAL → ACTIVE**
   - Type: Automatic
   - Processor: CustomerRegistrationProcessor
   - Criterion: None
   - Description: Customer registers and account becomes active

2. **ACTIVE → SUSPENDED**
   - Type: Manual
   - Processor: CustomerSuspensionProcessor
   - Criterion: None
   - Description: Customer account is suspended

3. **SUSPENDED → ACTIVE**
   - Type: Manual
   - Processor: CustomerReactivationProcessor
   - Criterion: CustomerReactivationCriterion
   - Description: Customer account is reactivated

4. **ACTIVE → BLACKLISTED**
   - Type: Manual
   - Processor: CustomerBlacklistProcessor
   - Criterion: None
   - Description: Customer is blacklisted

5. **SUSPENDED → BLACKLISTED**
   - Type: Manual
   - Processor: CustomerBlacklistProcessor
   - Criterion: None
   - Description: Suspended customer is blacklisted

```mermaid
stateDiagram-v2
    [*] --> INITIAL
    INITIAL --> ACTIVE : CustomerRegistrationProcessor
    ACTIVE --> SUSPENDED : CustomerSuspensionProcessor
    SUSPENDED --> ACTIVE : CustomerReactivationProcessor / CustomerReactivationCriterion
    ACTIVE --> BLACKLISTED : CustomerBlacklistProcessor
    SUSPENDED --> BLACKLISTED : CustomerBlacklistProcessor
```

---

## AdoptionApplication Workflow

**Name:** AdoptionApplicationWorkflow

**States:**
- INITIAL (starting state)
- SUBMITTED (application has been submitted)
- UNDER_REVIEW (application is being reviewed)
- APPROVED (application has been approved)
- REJECTED (application has been rejected)
- EXPIRED (application has expired)

**Transitions:**

1. **INITIAL → SUBMITTED**
   - Type: Automatic
   - Processor: ApplicationSubmissionProcessor
   - Criterion: None
   - Description: Application is submitted by customer

2. **SUBMITTED → UNDER_REVIEW**
   - Type: Manual
   - Processor: ApplicationReviewStartProcessor
   - Criterion: None
   - Description: Staff starts reviewing the application

3. **UNDER_REVIEW → APPROVED**
   - Type: Manual
   - Processor: ApplicationApprovalProcessor
   - Criterion: ApplicationApprovalCriterion
   - Description: Application is approved after review

4. **UNDER_REVIEW → REJECTED**
   - Type: Manual
   - Processor: ApplicationRejectionProcessor
   - Criterion: None
   - Description: Application is rejected after review

5. **SUBMITTED → EXPIRED**
   - Type: Manual
   - Processor: ApplicationExpirationProcessor
   - Criterion: None
   - Description: Application expires if not reviewed in time

6. **UNDER_REVIEW → EXPIRED**
   - Type: Manual
   - Processor: ApplicationExpirationProcessor
   - Criterion: None
   - Description: Application expires during review

```mermaid
stateDiagram-v2
    [*] --> INITIAL
    INITIAL --> SUBMITTED : ApplicationSubmissionProcessor
    SUBMITTED --> UNDER_REVIEW : ApplicationReviewStartProcessor
    UNDER_REVIEW --> APPROVED : ApplicationApprovalProcessor / ApplicationApprovalCriterion
    UNDER_REVIEW --> REJECTED : ApplicationRejectionProcessor
    SUBMITTED --> EXPIRED : ApplicationExpirationProcessor
    UNDER_REVIEW --> EXPIRED : ApplicationExpirationProcessor
```

---

## Adoption Workflow

**Name:** AdoptionWorkflow

**States:**
- INITIAL (starting state)
- COMPLETED (adoption has been completed)
- FOLLOW_UP_PENDING (follow-up is pending)
- FOLLOW_UP_COMPLETED (follow-up has been completed)
- RETURNED (pet has been returned)

**Transitions:**

1. **INITIAL → COMPLETED**
   - Type: Automatic
   - Processor: AdoptionCompletionProcessor
   - Criterion: None
   - Description: Adoption is completed

2. **COMPLETED → FOLLOW_UP_PENDING**
   - Type: Manual
   - Processor: FollowUpSchedulingProcessor
   - Criterion: None
   - Description: Follow-up is scheduled

3. **FOLLOW_UP_PENDING → FOLLOW_UP_COMPLETED**
   - Type: Manual
   - Processor: FollowUpCompletionProcessor
   - Criterion: None
   - Description: Follow-up is completed

4. **COMPLETED → RETURNED**
   - Type: Manual
   - Processor: AdoptionReturnProcessor
   - Criterion: None
   - Description: Pet is returned by adopter

5. **FOLLOW_UP_PENDING → RETURNED**
   - Type: Manual
   - Processor: AdoptionReturnProcessor
   - Criterion: None
   - Description: Pet is returned during follow-up period

6. **FOLLOW_UP_COMPLETED → RETURNED**
   - Type: Manual
   - Processor: AdoptionReturnProcessor
   - Criterion: None
   - Description: Pet is returned after follow-up completion

```mermaid
stateDiagram-v2
    [*] --> INITIAL
    INITIAL --> COMPLETED : AdoptionCompletionProcessor
    COMPLETED --> FOLLOW_UP_PENDING : FollowUpSchedulingProcessor
    FOLLOW_UP_PENDING --> FOLLOW_UP_COMPLETED : FollowUpCompletionProcessor
    COMPLETED --> RETURNED : AdoptionReturnProcessor
    FOLLOW_UP_PENDING --> RETURNED : AdoptionReturnProcessor
    FOLLOW_UP_COMPLETED --> RETURNED : AdoptionReturnProcessor
```
