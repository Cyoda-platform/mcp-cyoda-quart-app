# Entities for Purrfect Pets API

## Overview
The Purrfect Pets API manages pets, their owners, veterinarians, appointments, and medical records in a pet store/veterinary system.

## Entity Definitions

### 1. Pet Entity
**Name**: Pet
**Description**: Represents a pet in the system with basic information and health status.

**Attributes**:
- `pet_id` (string, required): Unique identifier for the pet
- `name` (string, required): Pet's name (max 100 characters)
- `species` (string, required): Type of animal (dog, cat, bird, fish, etc.)
- `breed` (string, optional): Specific breed of the pet
- `age` (integer, optional): Age in years
- `weight` (float, optional): Weight in kilograms
- `color` (string, optional): Primary color of the pet
- `gender` (string, optional): Male/Female/Unknown
- `microchip_id` (string, optional): Microchip identification number
- `owner_id` (string, required): Reference to the pet's owner
- `registration_date` (datetime, required): When the pet was registered
- `is_active` (boolean, required): Whether the pet is still active in the system
- `special_needs` (string, optional): Any special care requirements
- `photo_url` (string, optional): URL to pet's photo

**Relationships**:
- Belongs to one Owner (many-to-one)
- Has many Appointments (one-to-many)
- Has many MedicalRecords (one-to-many)

**Note**: Pet status/state is managed by the workflow system via entity.meta.state

### 2. Owner Entity
**Name**: Owner
**Description**: Represents a pet owner with contact information and preferences.

**Attributes**:
- `owner_id` (string, required): Unique identifier for the owner
- `first_name` (string, required): Owner's first name (max 50 characters)
- `last_name` (string, required): Owner's last name (max 50 characters)
- `email` (string, required): Email address (must be valid email format)
- `phone` (string, required): Primary phone number
- `address` (string, optional): Home address
- `city` (string, optional): City of residence
- `postal_code` (string, optional): Postal/ZIP code
- `emergency_contact_name` (string, optional): Emergency contact person
- `emergency_contact_phone` (string, optional): Emergency contact phone
- `registration_date` (datetime, required): When the owner registered
- `preferred_vet_id` (string, optional): Reference to preferred veterinarian
- `communication_preferences` (string, optional): Email/SMS/Phone preferences

**Relationships**:
- Has many Pets (one-to-many)
- Has many Appointments (one-to-many)
- May have a preferred Veterinarian (many-to-one, optional)

### 3. Veterinarian Entity
**Name**: Veterinarian
**Description**: Represents a veterinarian who can provide medical care to pets.

**Attributes**:
- `vet_id` (string, required): Unique identifier for the veterinarian
- `first_name` (string, required): Veterinarian's first name (max 50 characters)
- `last_name` (string, required): Veterinarian's last name (max 50 characters)
- `email` (string, required): Professional email address
- `phone` (string, required): Professional phone number
- `license_number` (string, required): Veterinary license number
- `specialization` (string, optional): Area of specialization
- `years_experience` (integer, optional): Years of veterinary experience
- `hire_date` (datetime, required): When the vet was hired
- `is_available` (boolean, required): Whether the vet is currently available
- `working_hours` (string, optional): Typical working schedule

**Relationships**:
- Has many Appointments (one-to-many)
- Has many MedicalRecords (one-to-many)
- May be preferred by many Owners (one-to-many)

### 4. Appointment Entity
**Name**: Appointment
**Description**: Represents a scheduled appointment between a pet, owner, and veterinarian.

**Attributes**:
- `appointment_id` (string, required): Unique identifier for the appointment
- `pet_id` (string, required): Reference to the pet
- `owner_id` (string, required): Reference to the owner
- `vet_id` (string, required): Reference to the veterinarian
- `appointment_date` (datetime, required): Scheduled date and time
- `duration_minutes` (integer, required): Expected duration in minutes
- `appointment_type` (string, required): Type of appointment (checkup, vaccination, surgery, etc.)
- `reason` (string, optional): Reason for the appointment
- `notes` (string, optional): Additional notes
- `created_date` (datetime, required): When the appointment was created
- `estimated_cost` (float, optional): Estimated cost of the appointment

**Relationships**:
- Belongs to one Pet (many-to-one)
- Belongs to one Owner (many-to-one)
- Belongs to one Veterinarian (many-to-one)
- May have one MedicalRecord (one-to-one, optional)

**Note**: Appointment status is managed by the workflow system via entity.meta.state

### 5. MedicalRecord Entity
**Name**: MedicalRecord
**Description**: Represents a medical record documenting a pet's health examination or treatment.

**Attributes**:
- `record_id` (string, required): Unique identifier for the medical record
- `pet_id` (string, required): Reference to the pet
- `vet_id` (string, required): Reference to the veterinarian
- `appointment_id` (string, optional): Reference to related appointment
- `visit_date` (datetime, required): Date of the medical visit
- `diagnosis` (string, optional): Medical diagnosis
- `treatment` (string, optional): Treatment provided
- `medications` (string, optional): Medications prescribed
- `notes` (string, optional): Additional medical notes
- `follow_up_required` (boolean, required): Whether follow-up is needed
- `follow_up_date` (datetime, optional): Recommended follow-up date
- `cost` (float, optional): Actual cost of the visit
- `created_date` (datetime, required): When the record was created

**Relationships**:
- Belongs to one Pet (many-to-one)
- Belongs to one Veterinarian (many-to-one)
- May belong to one Appointment (one-to-one, optional)

**Note**: Medical record status is managed by the workflow system via entity.meta.state
