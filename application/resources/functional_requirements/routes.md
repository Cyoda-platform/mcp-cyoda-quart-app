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
