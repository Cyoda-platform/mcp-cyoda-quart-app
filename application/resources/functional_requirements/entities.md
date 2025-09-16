# Entities for Purrfect Pets API

## Pet Entity

**Name:** Pet

**Attributes:**
- id: Long (unique identifier)
- name: String (pet's name)
- category: String (e.g., "Dog", "Cat", "Bird", "Fish")
- breed: String (specific breed)
- age: Integer (age in years)
- color: String (primary color)
- weight: Double (weight in kg)
- description: String (detailed description)
- price: Double (price in USD)
- imageUrl: String (URL to pet's photo)
- vaccinated: Boolean (vaccination status)
- neutered: Boolean (neutering status)
- microchipped: Boolean (microchip status)
- specialNeeds: String (any special care requirements)
- arrivalDate: LocalDateTime (when pet arrived at store)
- adopterId: Long (ID of adopter, null if not adopted)

**Relationships:**
- One Pet belongs to zero or one Customer (adopter)
- One Pet can have multiple PetCareRecords
- One Pet can have multiple AdoptionApplications

**State Management:**
The Pet entity uses `entity.meta.state` to track its lifecycle status. States include: AVAILABLE, RESERVED, ADOPTED, MEDICAL_HOLD, UNAVAILABLE.

---

## Customer Entity

**Name:** Customer

**Attributes:**
- id: Long (unique identifier)
- firstName: String (customer's first name)
- lastName: String (customer's last name)
- email: String (email address)
- phone: String (phone number)
- address: String (full address)
- city: String (city)
- state: String (state/province)
- zipCode: String (postal code)
- dateOfBirth: LocalDate (birth date)
- occupation: String (job title)
- housingType: String (e.g., "House", "Apartment", "Condo")
- hasYard: Boolean (has yard for pets)
- hasOtherPets: Boolean (owns other pets)
- petExperience: String (experience level with pets)
- preferredContactMethod: String (email, phone, text)
- registrationDate: LocalDateTime (when customer registered)

**Relationships:**
- One Customer can have multiple adopted Pets
- One Customer can have multiple AdoptionApplications
- One Customer can have multiple PetCareRecords (for their pets)

**State Management:**
The Customer entity uses `entity.meta.state` to track their status. States include: REGISTERED, VERIFIED, APPROVED, SUSPENDED, INACTIVE.

---

## AdoptionApplication Entity

**Name:** AdoptionApplication

**Attributes:**
- id: Long (unique identifier)
- customerId: Long (applicant customer ID)
- petId: Long (pet being applied for)
- applicationDate: LocalDateTime (when application was submitted)
- reasonForAdoption: String (why they want to adopt)
- livingArrangement: String (description of living situation)
- workSchedule: String (daily work schedule)
- petCareExperience: String (previous pet care experience)
- veterinarianContact: String (current vet contact info)
- references: String (personal references)
- agreedToTerms: Boolean (agreed to adoption terms)
- applicationFee: Double (application fee amount)
- notes: String (additional notes)
- reviewerId: Long (staff member reviewing application)
- reviewDate: LocalDateTime (when application was reviewed)
- rejectionReason: String (reason for rejection if applicable)

**Relationships:**
- One AdoptionApplication belongs to one Customer
- One AdoptionApplication is for one Pet
- One AdoptionApplication can be reviewed by one Staff member

**State Management:**
The AdoptionApplication entity uses `entity.meta.state` to track its processing status. States include: SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, WITHDRAWN.

---

## PetCareRecord Entity

**Name:** PetCareRecord

**Attributes:**
- id: Long (unique identifier)
- petId: Long (pet this record belongs to)
- careDate: LocalDateTime (date of care)
- careType: String (e.g., "Vaccination", "Checkup", "Treatment", "Grooming")
- description: String (detailed description of care)
- veterinarian: String (vet or staff member name)
- cost: Double (cost of care)
- nextDueDate: LocalDate (when next care is due)
- medications: String (any medications given)
- notes: String (additional notes)
- attachments: String (URLs to documents/photos)

**Relationships:**
- One PetCareRecord belongs to one Pet
- One PetCareRecord can be created by one Staff member

**State Management:**
The PetCareRecord entity uses `entity.meta.state` to track its status. States include: SCHEDULED, COMPLETED, CANCELLED.

---

## Staff Entity

**Name:** Staff

**Attributes:**
- id: Long (unique identifier)
- firstName: String (staff member's first name)
- lastName: String (staff member's last name)
- email: String (work email address)
- phone: String (work phone number)
- role: String (e.g., "Manager", "Veterinarian", "Caretaker", "Adoption Counselor")
- department: String (department name)
- hireDate: LocalDate (date of hire)
- salary: Double (annual salary)
- isActive: Boolean (employment status)
- certifications: String (relevant certifications)
- specializations: String (areas of expertise)

**Relationships:**
- One Staff member can review multiple AdoptionApplications
- One Staff member can create multiple PetCareRecords

**State Management:**
The Staff entity uses `entity.meta.state` to track their employment status. States include: ACTIVE, ON_LEAVE, SUSPENDED, TERMINATED.
