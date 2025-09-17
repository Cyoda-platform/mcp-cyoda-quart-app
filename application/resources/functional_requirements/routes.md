# Routes for Purrfect Pets API

## PetRoutes

### GET /api/pets
**Description:** Get all pets with optional filtering
**Parameters:** 
- category (optional): Filter by pet category
- state (optional): Filter by pet state
- storeId (optional): Filter by store ID
- available (optional): Filter only available pets

**Request Example:**
```
GET /api/pets?category=Dog&available=true&storeId=1
```

**Response Example:**
```json
{
  "pets": [
    {
      "id": 1,
      "name": "Buddy",
      "category": "Dog",
      "breed": "Golden Retriever",
      "age": 3,
      "state": "AVAILABLE"
    }
  ],
  "total": 1
}
```

### GET /api/pets/{id}
**Description:** Get a specific pet by ID

**Request Example:**
```
GET /api/pets/1
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Buddy",
  "category": "Dog",
  "breed": "Golden Retriever",
  "age": 3,
  "color": "Golden",
  "weight": 25.5,
  "description": "Friendly and energetic dog",
  "price": 250.00,
  "state": "AVAILABLE"
}
```

### POST /api/pets
**Description:** Create a new pet
**Transition:** INITIAL → AVAILABLE (automatic)

**Request Example:**
```json
{
  "name": "Buddy",
  "category": "Dog",
  "breed": "Golden Retriever",
  "age": 3,
  "color": "Golden",
  "weight": 25.5,
  "description": "Friendly and energetic dog",
  "price": 250.00,
  "vaccinated": true,
  "neutered": true,
  "microchipped": false,
  "storeId": 1
}
```

**Response Example:**
```json
{
  "id": 1,
  "name": "Buddy",
  "state": "AVAILABLE",
  "message": "Pet created successfully"
}
```

### PUT /api/pets/{id}
**Description:** Update a pet
**Parameters:**
- transitionName (optional): Name of the workflow transition to execute

**Request Example (with transition):**
```json
{
  "name": "Buddy Updated",
  "description": "Updated description",
  "transitionName": "AVAILABLE_TO_RESERVED",
  "customerId": 123,
  "applicationId": 456
}
```

**Request Example (without transition):**
```json
{
  "name": "Buddy Updated",
  "description": "Updated description",
  "price": 275.00
}
```

### PUT /api/pets/{id}/reserve
**Description:** Reserve a pet for adoption
**Transition:** AVAILABLE → RESERVED

**Request Example:**
```json
{
  "customerId": 123,
  "applicationId": 456,
  "transitionName": "AVAILABLE_TO_RESERVED"
}
```

### PUT /api/pets/{id}/adopt
**Description:** Complete pet adoption
**Transition:** RESERVED → ADOPTED

**Request Example:**
```json
{
  "adoptionFee": 250.00,
  "contractSigned": true,
  "microchipTransferred": true,
  "vaccinationRecordsProvided": true,
  "transitionName": "RESERVED_TO_ADOPTED"
}
```

### PUT /api/pets/{id}/medical-hold
**Description:** Place pet on medical hold
**Transition:** AVAILABLE → MEDICAL_HOLD

**Request Example:**
```json
{
  "medicalNotes": "Needs vaccination update",
  "expectedDuration": "7 days",
  "transitionName": "AVAILABLE_TO_MEDICAL_HOLD"
}
```

### PUT /api/pets/{id}/medical-clearance
**Description:** Clear pet from medical hold
**Transition:** MEDICAL_HOLD → AVAILABLE

**Request Example:**
```json
{
  "clearanceNotes": "Vaccination completed",
  "veterinarianApproval": true,
  "treatmentComplete": true,
  "transitionName": "MEDICAL_HOLD_TO_AVAILABLE"
}
```

### DELETE /api/pets/{id}
**Description:** Delete a pet (soft delete)

---

## StoreRoutes

### GET /api/stores
**Description:** Get all stores

**Request Example:**
```
GET /api/stores
```

**Response Example:**
```json
{
  "stores": [
    {
      "id": 1,
      "name": "Downtown Pet Store",
      "city": "New York",
      "state": "ACTIVE",
      "currentPetCount": 15
    }
  ]
}
```

### GET /api/stores/{id}
**Description:** Get a specific store by ID

### POST /api/stores
**Description:** Create a new store
**Transition:** INITIAL → ACTIVE (automatic)

**Request Example:**
```json
{
  "name": "Downtown Pet Store",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "zipCode": "10001",
  "phone": "555-0123",
  "email": "downtown@purrfectpets.com",
  "managerName": "John Smith",
  "openingHours": "Mon-Fri 9AM-6PM, Sat-Sun 10AM-4PM",
  "capacity": 50
}
```

### PUT /api/stores/{id}
**Description:** Update a store
**Parameters:**
- transitionName (optional): Name of the workflow transition to execute

**Request Example (with transition):**
```json
{
  "closureReason": "Renovation",
  "expectedReopeningDate": "2024-02-01",
  "transitionName": "ACTIVE_TO_TEMPORARILY_CLOSED"
}
```

### PUT /api/stores/{id}/close-temporarily
**Description:** Temporarily close a store
**Transition:** ACTIVE → TEMPORARILY_CLOSED

**Request Example:**
```json
{
  "closureReason": "Renovation",
  "expectedReopeningDate": "2024-02-01",
  "transitionName": "ACTIVE_TO_TEMPORARILY_CLOSED"
}
```

### PUT /api/stores/{id}/reopen
**Description:** Reopen a temporarily closed store
**Transition:** TEMPORARILY_CLOSED → ACTIVE

**Request Example:**
```json
{
  "reopeningNotes": "Renovation completed",
  "issuesResolved": true,
  "staffAvailable": true,
  "facilitiesReady": true,
  "transitionName": "TEMPORARILY_CLOSED_TO_ACTIVE"
}
```

---

## CustomerRoutes

### GET /api/customers
**Description:** Get all customers with optional filtering

### GET /api/customers/{id}
**Description:** Get a specific customer by ID

### POST /api/customers
**Description:** Create a new customer
**Transition:** INITIAL → ACTIVE (automatic)

**Request Example:**
```json
{
  "firstName": "Jane",
  "lastName": "Doe",
  "email": "jane.doe@email.com",
  "phone": "555-0123",
  "address": "456 Oak St",
  "city": "New York",
  "state": "NY",
  "zipCode": "10001",
  "dateOfBirth": "1990-05-15",
  "occupation": "Teacher",
  "housingType": "House",
  "hasYard": true,
  "hasOtherPets": false,
  "previousPetExperience": "Had dogs for 10 years"
}
```

### PUT /api/customers/{id}
**Description:** Update a customer
**Parameters:**
- transitionName (optional): Name of the workflow transition to execute

### PUT /api/customers/{id}/suspend
**Description:** Suspend a customer account
**Transition:** ACTIVE → SUSPENDED

**Request Example:**
```json
{
  "suspensionReason": "Policy violation",
  "transitionName": "ACTIVE_TO_SUSPENDED"
}
```

### PUT /api/customers/{id}/reactivate
**Description:** Reactivate a suspended customer account
**Transition:** SUSPENDED → ACTIVE

**Request Example:**
```json
{
  "issuesResolved": true,
  "agreesToTerms": true,
  "transitionName": "SUSPENDED_TO_ACTIVE"
}
```

### PUT /api/customers/{id}/blacklist
**Description:** Blacklist a customer
**Transition:** ACTIVE/SUSPENDED → BLACKLISTED

**Request Example:**
```json
{
  "blacklistReason": "Fraudulent activity",
  "transitionName": "ACTIVE_TO_BLACKLISTED"
}
```

---

## AdoptionApplicationRoutes

### GET /api/adoption-applications
**Description:** Get all adoption applications with optional filtering
**Parameters:**
- customerId (optional): Filter by customer ID
- petId (optional): Filter by pet ID
- storeId (optional): Filter by store ID
- state (optional): Filter by application state

**Request Example:**
```
GET /api/adoption-applications?customerId=123&state=UNDER_REVIEW
```

**Response Example:**
```json
{
  "applications": [
    {
      "id": 1,
      "customerId": 123,
      "petId": 456,
      "storeId": 1,
      "state": "UNDER_REVIEW",
      "applicationDate": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

### GET /api/adoption-applications/{id}
**Description:** Get a specific adoption application by ID

**Request Example:**
```
GET /api/adoption-applications/1
```

**Response Example:**
```json
{
  "id": 1,
  "customerId": 123,
  "petId": 456,
  "storeId": 1,
  "applicationDate": "2024-01-15T10:30:00Z",
  "preferredPickupDate": "2024-01-25",
  "reasonForAdoption": "Looking for a family companion",
  "livingArrangement": "Single family home with yard",
  "workSchedule": "9-5 weekdays, home evenings and weekends",
  "petCareExperience": "Had dogs for 15 years",
  "veterinarianContact": "Dr. Smith - 555-0199",
  "references": "John Doe - 555-0188, Jane Smith - 555-0177",
  "state": "UNDER_REVIEW"
}
```

### POST /api/adoption-applications
**Description:** Create a new adoption application
**Transition:** INITIAL → SUBMITTED (automatic)

**Request Example:**
```json
{
  "customerId": 123,
  "petId": 456,
  "storeId": 1,
  "preferredPickupDate": "2024-01-25",
  "reasonForAdoption": "Looking for a family companion",
  "livingArrangement": "Single family home with yard",
  "workSchedule": "9-5 weekdays, home evenings and weekends",
  "petCareExperience": "Had dogs for 15 years",
  "veterinarianContact": "Dr. Smith - 555-0199",
  "references": "John Doe - 555-0188, Jane Smith - 555-0177"
}
```

**Response Example:**
```json
{
  "id": 1,
  "state": "SUBMITTED",
  "message": "Adoption application submitted successfully"
}
```

### PUT /api/adoption-applications/{id}
**Description:** Update an adoption application
**Parameters:**
- transitionName (optional): Name of the workflow transition to execute

**Request Example (without transition):**
```json
{
  "reasonForAdoption": "Updated reason",
  "applicationNotes": "Additional notes"
}
```

### PUT /api/adoption-applications/{id}/start-review
**Description:** Start reviewing an adoption application
**Transition:** SUBMITTED → UNDER_REVIEW

**Request Example:**
```json
{
  "reviewerId": 789,
  "reviewerName": "Staff Member",
  "transitionName": "SUBMITTED_TO_UNDER_REVIEW"
}
```

### PUT /api/adoption-applications/{id}/approve
**Description:** Approve an adoption application
**Transition:** UNDER_REVIEW → APPROVED

**Request Example:**
```json
{
  "approvalNotes": "All requirements met",
  "reviewerId": 789,
  "backgroundCheckPassed": true,
  "referencesVerified": true,
  "housingApproved": true,
  "petCompatibilityConfirmed": true,
  "transitionName": "UNDER_REVIEW_TO_APPROVED"
}
```

### PUT /api/adoption-applications/{id}/reject
**Description:** Reject an adoption application
**Transition:** UNDER_REVIEW → REJECTED

**Request Example:**
```json
{
  "rejectionReason": "Housing not suitable for this pet",
  "reviewerId": 789,
  "transitionName": "UNDER_REVIEW_TO_REJECTED"
}
```

### PUT /api/adoption-applications/{id}/expire
**Description:** Expire an adoption application
**Transition:** SUBMITTED/UNDER_REVIEW → EXPIRED

**Request Example:**
```json
{
  "expirationReason": "Application exceeded time limit",
  "transitionName": "SUBMITTED_TO_EXPIRED"
}
```

---

## AdoptionRoutes

### GET /api/adoptions
**Description:** Get all adoptions with optional filtering
**Parameters:**
- customerId (optional): Filter by customer ID
- petId (optional): Filter by pet ID
- storeId (optional): Filter by store ID
- state (optional): Filter by adoption state

**Request Example:**
```
GET /api/adoptions?customerId=123&state=COMPLETED
```

**Response Example:**
```json
{
  "adoptions": [
    {
      "id": 1,
      "customerId": 123,
      "petId": 456,
      "storeId": 1,
      "adoptionDate": "2024-01-20T14:30:00Z",
      "state": "COMPLETED"
    }
  ],
  "total": 1
}
```

### GET /api/adoptions/{id}
**Description:** Get a specific adoption by ID

**Request Example:**
```
GET /api/adoptions/1
```

**Response Example:**
```json
{
  "id": 1,
  "customerId": 123,
  "petId": 456,
  "storeId": 1,
  "applicationId": 789,
  "adoptionDate": "2024-01-20T14:30:00Z",
  "adoptionFee": 250.00,
  "contractSigned": true,
  "microchipTransferred": true,
  "vaccinationRecordsProvided": true,
  "followUpDate": "2024-02-20",
  "state": "COMPLETED"
}
```

### POST /api/adoptions
**Description:** Create a new adoption record
**Transition:** INITIAL → COMPLETED (automatic)

**Request Example:**
```json
{
  "customerId": 123,
  "petId": 456,
  "storeId": 1,
  "applicationId": 789,
  "adoptionFee": 250.00,
  "contractSigned": true,
  "microchipTransferred": true,
  "vaccinationRecordsProvided": true,
  "adoptionNotes": "Smooth adoption process"
}
```

**Response Example:**
```json
{
  "id": 1,
  "state": "COMPLETED",
  "message": "Adoption completed successfully"
}
```

### PUT /api/adoptions/{id}
**Description:** Update an adoption record
**Parameters:**
- transitionName (optional): Name of the workflow transition to execute

### PUT /api/adoptions/{id}/schedule-followup
**Description:** Schedule a follow-up for an adoption
**Transition:** COMPLETED → FOLLOW_UP_PENDING

**Request Example:**
```json
{
  "followUpDate": "2024-02-20",
  "followUpNotes": "Check on pet adjustment",
  "transitionName": "COMPLETED_TO_FOLLOW_UP_PENDING"
}
```

### PUT /api/adoptions/{id}/complete-followup
**Description:** Complete a follow-up for an adoption
**Transition:** FOLLOW_UP_PENDING → FOLLOW_UP_COMPLETED

**Request Example:**
```json
{
  "followUpNotes": "Pet is well adjusted, customer is happy",
  "followUpCompleted": true,
  "transitionName": "FOLLOW_UP_PENDING_TO_FOLLOW_UP_COMPLETED"
}
```

### PUT /api/adoptions/{id}/return
**Description:** Process the return of an adopted pet
**Transition:** COMPLETED/FOLLOW_UP_PENDING/FOLLOW_UP_COMPLETED → RETURNED

**Request Example:**
```json
{
  "returnReason": "Pet not compatible with family lifestyle",
  "returnDate": "2024-02-15T10:00:00Z",
  "transitionName": "COMPLETED_TO_RETURNED"
}
```
