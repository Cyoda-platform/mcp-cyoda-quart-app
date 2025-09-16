# Routes for Purrfect Pets API

## PetRoutes

### GET /api/pets
**Description:** Get all pets with optional filtering
**Parameters:**
- category (optional): Filter by pet category
- state (optional): Filter by pet state
- minPrice (optional): Minimum price filter
- maxPrice (optional): Maximum price filter
- page (optional): Page number for pagination
- size (optional): Page size for pagination

**Request Example:**
```
GET /api/pets?category=Dog&state=AVAILABLE&page=0&size=10
```

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "name": "Buddy",
      "category": "Dog",
      "breed": "Golden Retriever",
      "age": 3,
      "price": 250.0,
      "state": "AVAILABLE"
    }
  ],
  "totalElements": 25,
  "totalPages": 3
}
```

### GET /api/pets/{id}
**Description:** Get pet by ID
**Parameters:**
- id: Pet ID

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
  "price": 250.0,
  "imageUrl": "https://example.com/buddy.jpg",
  "vaccinated": true,
  "neutered": true,
  "microchipped": true,
  "state": "AVAILABLE"
}
```

### POST /api/pets
**Description:** Create new pet
**Parameters:**
- transitionName: null (automatic transition to AVAILABLE)

**Request Example:**
```json
{
  "name": "Max",
  "category": "Dog",
  "breed": "Labrador",
  "age": 2,
  "color": "Black",
  "weight": 30.0,
  "description": "Playful and loyal companion",
  "price": 300.0,
  "vaccinated": true,
  "neutered": false,
  "microchipped": true,
  "transitionName": null
}
```

### PUT /api/pets/{id}
**Description:** Update pet information
**Parameters:**
- id: Pet ID
- transitionName: Transition name for state change (optional)

**Request Example:**
```json
{
  "name": "Max Updated",
  "description": "Updated description",
  "price": 280.0,
  "transitionName": "AVAILABLE_TO_RESERVED"
}
```

### PUT /api/pets/{id}/reserve
**Description:** Reserve pet for customer
**Parameters:**
- id: Pet ID
- customerId: Customer ID
- transitionName: "AVAILABLE_TO_RESERVED"

**Request Example:**
```json
{
  "customerId": 123,
  "transitionName": "AVAILABLE_TO_RESERVED"
}
```

### PUT /api/pets/{id}/adopt
**Description:** Complete pet adoption
**Parameters:**
- id: Pet ID
- applicationId: Adoption application ID
- transitionName: "RESERVED_TO_ADOPTED"

**Request Example:**
```json
{
  "applicationId": 456,
  "transitionName": "RESERVED_TO_ADOPTED"
}
```

### PUT /api/pets/{id}/medical-hold
**Description:** Put pet on medical hold
**Parameters:**
- id: Pet ID
- reason: Medical hold reason
- transitionName: "AVAILABLE_TO_MEDICAL_HOLD"

**Request Example:**
```json
{
  "reason": "Requires vaccination update",
  "transitionName": "AVAILABLE_TO_MEDICAL_HOLD"
}
```

### DELETE /api/pets/{id}
**Description:** Delete pet record

---

## CustomerRoutes

### GET /api/customers
**Description:** Get all customers with optional filtering
**Parameters:**
- state (optional): Filter by customer state
- city (optional): Filter by city
- page (optional): Page number
- size (optional): Page size

**Request Example:**
```
GET /api/customers?state=APPROVED&page=0&size=20
```

**Response Example:**
```json
{
  "content": [
    {
      "id": 1,
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@email.com",
      "phone": "555-1234",
      "state": "APPROVED"
    }
  ]
}
```

### GET /api/customers/{id}
**Description:** Get customer by ID

### POST /api/customers
**Description:** Register new customer
**Parameters:**
- transitionName: null (automatic transition to REGISTERED)

**Request Example:**
```json
{
  "firstName": "Jane",
  "lastName": "Smith",
  "email": "jane.smith@email.com",
  "phone": "555-5678",
  "address": "123 Main St",
  "city": "Anytown",
  "state": "CA",
  "zipCode": "12345",
  "dateOfBirth": "1990-05-15",
  "occupation": "Teacher",
  "housingType": "House",
  "hasYard": true,
  "hasOtherPets": false,
  "petExperience": "Beginner",
  "preferredContactMethod": "email",
  "transitionName": null
}
```

### PUT /api/customers/{id}
**Description:** Update customer information
**Parameters:**
- transitionName: Transition name for state change (optional)

### PUT /api/customers/{id}/verify
**Description:** Verify customer
**Parameters:**
- transitionName: "REGISTERED_TO_VERIFIED"

**Request Example:**
```json
{
  "verificationDocuments": ["id_copy.pdf", "address_proof.pdf"],
  "transitionName": "REGISTERED_TO_VERIFIED"
}
```

### PUT /api/customers/{id}/approve
**Description:** Approve customer for adoptions
**Parameters:**
- transitionName: "VERIFIED_TO_APPROVED"

**Request Example:**
```json
{
  "transitionName": "VERIFIED_TO_APPROVED"
}
```

### PUT /api/customers/{id}/suspend
**Description:** Suspend customer account
**Parameters:**
- reason: Suspension reason
- transitionName: "APPROVED_TO_SUSPENDED"

**Request Example:**
```json
{
  "reason": "Policy violation",
  "transitionName": "APPROVED_TO_SUSPENDED"
}
```

---

## AdoptionApplicationRoutes

### GET /api/adoption-applications
**Description:** Get all adoption applications
**Parameters:**
- customerId (optional): Filter by customer
- petId (optional): Filter by pet
- state (optional): Filter by application state

**Request Example:**
```
GET /api/adoption-applications?customerId=123&state=UNDER_REVIEW
```

### GET /api/adoption-applications/{id}
**Description:** Get adoption application by ID

### POST /api/adoption-applications
**Description:** Submit new adoption application
**Parameters:**
- transitionName: null (automatic transition to SUBMITTED)

**Request Example:**
```json
{
  "customerId": 123,
  "petId": 456,
  "reasonForAdoption": "Looking for a family companion",
  "livingArrangement": "Single family home with large yard",
  "workSchedule": "9-5 weekdays, home evenings and weekends",
  "petCareExperience": "Had dogs for 10 years",
  "veterinarianContact": "Dr. Smith, Animal Hospital, 555-9999",
  "references": "Mary Johnson (555-1111), Bob Wilson (555-2222)",
  "agreedToTerms": true,
  "applicationFee": 50.0,
  "transitionName": null
}
```

### PUT /api/adoption-applications/{id}/start-review
**Description:** Start application review
**Parameters:**
- reviewerId: Staff member ID
- transitionName: "SUBMITTED_TO_UNDER_REVIEW"

**Request Example:**
```json
{
  "reviewerId": 789,
  "transitionName": "SUBMITTED_TO_UNDER_REVIEW"
}
```

### PUT /api/adoption-applications/{id}/approve
**Description:** Approve adoption application
**Parameters:**
- transitionName: "UNDER_REVIEW_TO_APPROVED"

**Request Example:**
```json
{
  "notes": "Excellent candidate, all checks passed",
  "transitionName": "UNDER_REVIEW_TO_APPROVED"
}
```

### PUT /api/adoption-applications/{id}/reject
**Description:** Reject adoption application
**Parameters:**
- rejectionReason: Reason for rejection
- transitionName: "UNDER_REVIEW_TO_REJECTED"

**Request Example:**
```json
{
  "rejectionReason": "Insufficient pet care experience",
  "transitionName": "UNDER_REVIEW_TO_REJECTED"
}
```

### PUT /api/adoption-applications/{id}/withdraw
**Description:** Withdraw adoption application
**Parameters:**
- transitionName: "SUBMITTED_TO_WITHDRAWN" or "UNDER_REVIEW_TO_WITHDRAWN"

**Request Example:**
```json
{
  "transitionName": "SUBMITTED_TO_WITHDRAWN"
}
```

---

## PetCareRecordRoutes

### GET /api/pet-care-records
**Description:** Get all pet care records
**Parameters:**
- petId (optional): Filter by pet
- careType (optional): Filter by care type
- state (optional): Filter by record state

### GET /api/pet-care-records/{id}
**Description:** Get pet care record by ID

### POST /api/pet-care-records
**Description:** Schedule new pet care
**Parameters:**
- transitionName: null (automatic transition to SCHEDULED)

**Request Example:**
```json
{
  "petId": 123,
  "careType": "Vaccination",
  "description": "Annual vaccination update",
  "veterinarian": "Dr. Johnson",
  "careDate": "2024-01-15T10:00:00",
  "transitionName": null
}
```

### PUT /api/pet-care-records/{id}/complete
**Description:** Mark care as completed
**Parameters:**
- transitionName: "SCHEDULED_TO_COMPLETED"

**Request Example:**
```json
{
  "cost": 75.0,
  "medications": "Rabies vaccine, DHPP vaccine",
  "notes": "Pet responded well to vaccinations",
  "nextDueDate": "2025-01-15",
  "transitionName": "SCHEDULED_TO_COMPLETED"
}
```

### PUT /api/pet-care-records/{id}/cancel
**Description:** Cancel scheduled care
**Parameters:**
- cancellationReason: Reason for cancellation
- transitionName: "SCHEDULED_TO_CANCELLED"

**Request Example:**
```json
{
  "cancellationReason": "Pet was adopted",
  "transitionName": "SCHEDULED_TO_CANCELLED"
}
```

---

## StaffRoutes

### GET /api/staff
**Description:** Get all staff members
**Parameters:**
- role (optional): Filter by role
- department (optional): Filter by department
- state (optional): Filter by staff state

### GET /api/staff/{id}
**Description:** Get staff member by ID

### POST /api/staff
**Description:** Add new staff member
**Parameters:**
- transitionName: null (automatic transition to ACTIVE)

**Request Example:**
```json
{
  "firstName": "Sarah",
  "lastName": "Johnson",
  "email": "sarah.johnson@purrfectpets.com",
  "phone": "555-7890",
  "role": "Veterinarian",
  "department": "Medical",
  "hireDate": "2024-01-01",
  "salary": 75000.0,
  "certifications": "DVM, State License #12345",
  "specializations": "Small animal medicine",
  "transitionName": null
}
```

### PUT /api/staff/{id}/leave
**Description:** Put staff member on leave
**Parameters:**
- leaveStartDate: Start date of leave
- leaveEndDate: End date of leave
- leaveReason: Reason for leave
- transitionName: "ACTIVE_TO_ON_LEAVE"

**Request Example:**
```json
{
  "leaveStartDate": "2024-02-01",
  "leaveEndDate": "2024-02-15",
  "leaveReason": "Medical leave",
  "transitionName": "ACTIVE_TO_ON_LEAVE"
}
```

### PUT /api/staff/{id}/return
**Description:** Return staff member from leave
**Parameters:**
- transitionName: "ON_LEAVE_TO_ACTIVE"

**Request Example:**
```json
{
  "returnDate": "2024-02-16",
  "transitionName": "ON_LEAVE_TO_ACTIVE"
}
```
