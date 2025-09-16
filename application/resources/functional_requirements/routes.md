# Routes for Purrfect Pets API

## Overview
The Purrfect Pets API provides RESTful endpoints for managing pets, owners, veterinarians, appointments, and medical records. Each entity has its own routes class.

## 1. PetRoutes

### Base Path: `/pets`

#### GET /pets
**Description**: Get all pets with optional filtering
**Query Parameters**:
- `species` (optional): Filter by pet species
- `owner_id` (optional): Filter by owner ID
- `is_active` (optional): Filter by active status (true/false)
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of items per page (default: 20)

**Request Example**:
```
GET /pets?species=dog&is_active=true&page=1&limit=10
```

**Response Example**:
```json
{
  "pets": [
    {
      "pet_id": "pet-123",
      "name": "Buddy",
      "species": "dog",
      "breed": "Golden Retriever",
      "age": 3,
      "owner_id": "owner-456",
      "state": "active"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

#### GET /pets/{pet_id}
**Description**: Get a specific pet by ID

**Request Example**:
```
GET /pets/pet-123
```

**Response Example**:
```json
{
  "pet_id": "pet-123",
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age": 3,
  "weight": 25.5,
  "color": "golden",
  "gender": "male",
  "owner_id": "owner-456",
  "registration_date": "2024-01-15T10:30:00Z",
  "is_active": true,
  "state": "active"
}
```

#### POST /pets
**Description**: Create a new pet
**Transition**: Triggers initial → registered → active workflow

**Request Example**:
```json
{
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age": 3,
  "weight": 25.5,
  "color": "golden",
  "gender": "male",
  "owner_id": "owner-456",
  "special_needs": "None"
}
```

**Response Example**:
```json
{
  "pet_id": "pet-123",
  "name": "Buddy",
  "species": "dog",
  "state": "active",
  "message": "Pet registered and activated successfully"
}
```

#### PUT /pets/{pet_id}
**Description**: Update a pet
**Query Parameters**:
- `transition` (optional): Transition name for state change

**Request Example** (with state transition):
```
PUT /pets/pet-123?transition=deactivate
```
```json
{
  "special_needs": "Requires medication",
  "weight": 26.0
}
```

**Response Example**:
```json
{
  "pet_id": "pet-123",
  "state": "inactive",
  "message": "Pet updated and deactivated successfully"
}
```

#### DELETE /pets/{pet_id}
**Description**: Archive a pet
**Transition**: archive

**Request Example**:
```
DELETE /pets/pet-123
```

**Response Example**:
```json
{
  "pet_id": "pet-123",
  "state": "archived",
  "message": "Pet archived successfully"
}
```

## 2. OwnerRoutes

### Base Path: `/owners`

#### GET /owners
**Description**: Get all owners with optional filtering
**Query Parameters**:
- `city` (optional): Filter by city
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page

**Request Example**:
```
GET /owners?city=New York&page=1&limit=10
```

**Response Example**:
```json
{
  "owners": [
    {
      "owner_id": "owner-456",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@email.com",
      "phone": "+1234567890",
      "city": "New York",
      "state": "active"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

#### GET /owners/{owner_id}
**Description**: Get a specific owner by ID

**Request Example**:
```
GET /owners/owner-456
```

**Response Example**:
```json
{
  "owner_id": "owner-456",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "New York",
  "postal_code": "10001",
  "registration_date": "2024-01-10T09:00:00Z",
  "state": "active"
}
```

#### POST /owners
**Description**: Create a new owner
**Transition**: Triggers initial → registered → verified → active workflow

**Request Example**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "New York",
  "postal_code": "10001",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+1234567891"
}
```

**Response Example**:
```json
{
  "owner_id": "owner-456",
  "first_name": "John",
  "last_name": "Doe",
  "state": "active",
  "message": "Owner registered and activated successfully"
}
```

#### PUT /owners/{owner_id}
**Description**: Update an owner
**Query Parameters**:
- `transition` (optional): Transition name for state change

**Request Example** (with state transition):
```
PUT /owners/owner-456?transition=suspend
```
```json
{
  "phone": "+1234567899",
  "address": "456 Oak St"
}
```

**Response Example**:
```json
{
  "owner_id": "owner-456",
  "state": "suspended",
  "message": "Owner updated and suspended successfully"
}
```

## 3. VeterinarianRoutes

### Base Path: `/veterinarians`

#### GET /veterinarians
**Description**: Get all veterinarians with optional filtering
**Query Parameters**:
- `specialization` (optional): Filter by specialization
- `is_available` (optional): Filter by availability (true/false)
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page

**Request Example**:
```
GET /veterinarians?specialization=surgery&is_available=true&page=1&limit=10
```

**Response Example**:
```json
{
  "veterinarians": [
    {
      "vet_id": "vet-789",
      "first_name": "Dr. Sarah",
      "last_name": "Smith",
      "specialization": "surgery",
      "is_available": true,
      "state": "active"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

#### POST /veterinarians
**Description**: Create a new veterinarian
**Transition**: Triggers initial → hired → licensed → active workflow

**Request Example**:
```json
{
  "first_name": "Sarah",
  "last_name": "Smith",
  "email": "sarah.smith@vetclinic.com",
  "phone": "+1234567892",
  "license_number": "VET123456",
  "specialization": "surgery",
  "years_experience": 8,
  "working_hours": "Mon-Fri 9AM-5PM"
}
```

**Response Example**:
```json
{
  "vet_id": "vet-789",
  "first_name": "Sarah",
  "last_name": "Smith",
  "state": "active",
  "message": "Veterinarian hired and activated successfully"
}
```

#### PUT /veterinarians/{vet_id}
**Description**: Update a veterinarian
**Query Parameters**:
- `transition` (optional): Transition name for state change

**Request Example** (with state transition):
```
PUT /veterinarians/vet-789?transition=unavailable
```
```json
{
  "working_hours": "Mon-Wed 9AM-3PM",
  "specialization": "surgery, emergency"
}
```

**Response Example**:
```json
{
  "vet_id": "vet-789",
  "state": "unavailable",
  "message": "Veterinarian updated and marked unavailable"
}
```

## 4. AppointmentRoutes

### Base Path: `/appointments`

#### GET /appointments
**Description**: Get all appointments with optional filtering
**Query Parameters**:
- `pet_id` (optional): Filter by pet ID
- `owner_id` (optional): Filter by owner ID
- `vet_id` (optional): Filter by veterinarian ID
- `date_from` (optional): Filter appointments from date (ISO format)
- `date_to` (optional): Filter appointments to date (ISO format)
- `appointment_type` (optional): Filter by appointment type
- `state` (optional): Filter by appointment state
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page

**Request Example**:
```
GET /appointments?vet_id=vet-789&date_from=2024-01-20&state=confirmed&page=1&limit=10
```

**Response Example**:
```json
{
  "appointments": [
    {
      "appointment_id": "appt-101",
      "pet_id": "pet-123",
      "owner_id": "owner-456",
      "vet_id": "vet-789",
      "appointment_date": "2024-01-25T14:00:00Z",
      "appointment_type": "checkup",
      "state": "confirmed"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

#### GET /appointments/{appointment_id}
**Description**: Get a specific appointment by ID

**Request Example**:
```
GET /appointments/appt-101
```

**Response Example**:
```json
{
  "appointment_id": "appt-101",
  "pet_id": "pet-123",
  "owner_id": "owner-456",
  "vet_id": "vet-789",
  "appointment_date": "2024-01-25T14:00:00Z",
  "duration_minutes": 30,
  "appointment_type": "checkup",
  "reason": "Annual checkup",
  "notes": "Regular health examination",
  "created_date": "2024-01-20T10:00:00Z",
  "estimated_cost": 75.00,
  "state": "confirmed"
}
```

#### POST /appointments
**Description**: Create a new appointment
**Transition**: Triggers initial → scheduled workflow

**Request Example**:
```json
{
  "pet_id": "pet-123",
  "owner_id": "owner-456",
  "vet_id": "vet-789",
  "appointment_date": "2024-01-25T14:00:00Z",
  "duration_minutes": 30,
  "appointment_type": "checkup",
  "reason": "Annual checkup",
  "notes": "Regular health examination",
  "estimated_cost": 75.00
}
```

**Response Example**:
```json
{
  "appointment_id": "appt-101",
  "pet_id": "pet-123",
  "appointment_date": "2024-01-25T14:00:00Z",
  "state": "scheduled",
  "message": "Appointment scheduled successfully"
}
```

#### PUT /appointments/{appointment_id}
**Description**: Update an appointment
**Query Parameters**:
- `transition` (optional): Transition name for state change (confirm, start, complete, cancel, no_show)

**Request Example** (with state transition):
```
PUT /appointments/appt-101?transition=confirm
```
```json
{
  "notes": "Updated notes for appointment",
  "estimated_cost": 80.00
}
```

**Response Example**:
```json
{
  "appointment_id": "appt-101",
  "state": "confirmed",
  "message": "Appointment updated and confirmed successfully"
}
```

#### DELETE /appointments/{appointment_id}
**Description**: Cancel an appointment
**Transition**: cancel

**Request Example**:
```
DELETE /appointments/appt-101
```

**Response Example**:
```json
{
  "appointment_id": "appt-101",
  "state": "cancelled",
  "message": "Appointment cancelled successfully"
}
```

## 5. MedicalRecordRoutes

### Base Path: `/medical-records`

#### GET /medical-records
**Description**: Get all medical records with optional filtering
**Query Parameters**:
- `pet_id` (optional): Filter by pet ID
- `vet_id` (optional): Filter by veterinarian ID
- `appointment_id` (optional): Filter by appointment ID
- `date_from` (optional): Filter records from date (ISO format)
- `date_to` (optional): Filter records to date (ISO format)
- `follow_up_required` (optional): Filter by follow-up requirement (true/false)
- `state` (optional): Filter by record state
- `page` (optional): Page number for pagination
- `limit` (optional): Number of items per page

**Request Example**:
```
GET /medical-records?pet_id=pet-123&follow_up_required=true&page=1&limit=10
```

**Response Example**:
```json
{
  "medical_records": [
    {
      "record_id": "record-201",
      "pet_id": "pet-123",
      "vet_id": "vet-789",
      "visit_date": "2024-01-25T14:30:00Z",
      "diagnosis": "Healthy",
      "follow_up_required": true,
      "state": "completed"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

#### GET /medical-records/{record_id}
**Description**: Get a specific medical record by ID

**Request Example**:
```
GET /medical-records/record-201
```

**Response Example**:
```json
{
  "record_id": "record-201",
  "pet_id": "pet-123",
  "vet_id": "vet-789",
  "appointment_id": "appt-101",
  "visit_date": "2024-01-25T14:30:00Z",
  "diagnosis": "Healthy, minor ear infection",
  "treatment": "Ear cleaning and antibiotic drops",
  "medications": "Antibiotic ear drops - 2 drops twice daily for 7 days",
  "notes": "Pet responded well to examination. Owner educated on ear care.",
  "follow_up_required": true,
  "follow_up_date": "2024-02-08T14:00:00Z",
  "cost": 85.00,
  "created_date": "2024-01-25T15:00:00Z",
  "state": "completed"
}
```

#### POST /medical-records
**Description**: Create a new medical record
**Transition**: Triggers initial → draft workflow

**Request Example**:
```json
{
  "pet_id": "pet-123",
  "vet_id": "vet-789",
  "appointment_id": "appt-101",
  "visit_date": "2024-01-25T14:30:00Z",
  "diagnosis": "Healthy, minor ear infection",
  "treatment": "Ear cleaning and antibiotic drops",
  "medications": "Antibiotic ear drops - 2 drops twice daily for 7 days",
  "notes": "Pet responded well to examination",
  "follow_up_required": true,
  "follow_up_date": "2024-02-08T14:00:00Z",
  "cost": 85.00
}
```

**Response Example**:
```json
{
  "record_id": "record-201",
  "pet_id": "pet-123",
  "visit_date": "2024-01-25T14:30:00Z",
  "state": "draft",
  "message": "Medical record created in draft state"
}
```

#### PUT /medical-records/{record_id}
**Description**: Update a medical record
**Query Parameters**:
- `transition` (optional): Transition name for state change (complete, review, archive, update)

**Request Example** (with state transition):
```
PUT /medical-records/record-201?transition=complete
```
```json
{
  "notes": "Updated notes after follow-up call with owner",
  "cost": 90.00
}
```

**Response Example**:
```json
{
  "record_id": "record-201",
  "state": "completed",
  "message": "Medical record updated and completed successfully"
}
```

## Common Response Patterns

### Error Responses
All endpoints return consistent error responses:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Pet with ID pet-999 not found",
  "timestamp": "2024-01-20T10:00:00Z"
}
```

### Pagination
All list endpoints support pagination with consistent response format:

```json
{
  "data": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "total_pages": 5
}
```

### State Transitions
When using transition parameters, the response includes the new state and a descriptive message about the transition that occurred.
