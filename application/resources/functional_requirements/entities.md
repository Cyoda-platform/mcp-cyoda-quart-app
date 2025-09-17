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
- adoptionDate: LocalDateTime (when pet was adopted, null if not adopted)

**Relationships:**
- One Pet belongs to one Store
- One Pet can have many AdoptionApplications
- One Pet can have one current Adoption (when adopted)

**State Management:**
The Pet entity uses `entity.meta.state` to track its lifecycle status. States include: AVAILABLE, RESERVED, ADOPTED, MEDICAL_HOLD, UNAVAILABLE.

---

## Store Entity

**Name:** Store

**Attributes:**
- id: Long (unique identifier)
- name: String (store name)
- address: String (full address)
- city: String
- state: String
- zipCode: String
- phone: String (contact phone)
- email: String (contact email)
- managerName: String (store manager's name)
- openingHours: String (e.g., "Mon-Fri 9AM-6PM")
- capacity: Integer (maximum number of pets)
- currentPetCount: Integer (current number of pets)

**Relationships:**
- One Store has many Pets
- One Store has many AdoptionApplications
- One Store has many Adoptions

**State Management:**
The Store entity uses `entity.meta.state` to track operational status. States include: ACTIVE, TEMPORARILY_CLOSED, PERMANENTLY_CLOSED.

---

## Customer Entity

**Name:** Customer

**Attributes:**
- id: Long (unique identifier)
- firstName: String
- lastName: String
- email: String (unique)
- phone: String
- address: String
- city: String
- state: String
- zipCode: String
- dateOfBirth: LocalDate
- occupation: String
- housingType: String (e.g., "House", "Apartment", "Condo")
- hasYard: Boolean
- hasOtherPets: Boolean
- otherPetsDescription: String
- previousPetExperience: String
- registrationDate: LocalDateTime

**Relationships:**
- One Customer can have many AdoptionApplications
- One Customer can have many Adoptions

**State Management:**
The Customer entity uses `entity.meta.state` to track account status. States include: ACTIVE, SUSPENDED, BLACKLISTED.

---

## AdoptionApplication Entity

**Name:** AdoptionApplication

**Attributes:**
- id: Long (unique identifier)
- customerId: Long (foreign key)
- petId: Long (foreign key)
- storeId: Long (foreign key)
- applicationDate: LocalDateTime
- preferredPickupDate: LocalDate
- reasonForAdoption: String
- livingArrangement: String
- workSchedule: String
- petCareExperience: String
- veterinarianContact: String
- references: String (contact information for references)
- applicationNotes: String
- reviewNotes: String (staff notes during review)
- rejectionReason: String (if rejected)
- approvalDate: LocalDateTime
- rejectionDate: LocalDateTime

**Relationships:**
- One AdoptionApplication belongs to one Customer
- One AdoptionApplication belongs to one Pet
- One AdoptionApplication belongs to one Store

**State Management:**
The AdoptionApplication entity uses `entity.meta.state` to track application progress. States include: SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, EXPIRED.

---

## Adoption Entity

**Name:** Adoption

**Attributes:**
- id: Long (unique identifier)
- customerId: Long (foreign key)
- petId: Long (foreign key)
- storeId: Long (foreign key)
- applicationId: Long (foreign key)
- adoptionDate: LocalDateTime
- adoptionFee: Double
- contractSigned: Boolean
- microchipTransferred: Boolean
- vaccinationRecordsProvided: Boolean
- followUpDate: LocalDate (scheduled follow-up)
- followUpCompleted: Boolean
- adoptionNotes: String
- returnDate: LocalDateTime (if pet is returned)
- returnReason: String (if pet is returned)

**Relationships:**
- One Adoption belongs to one Customer
- One Adoption belongs to one Pet
- One Adoption belongs to one Store
- One Adoption is created from one AdoptionApplication

**State Management:**
The Adoption entity uses `entity.meta.state` to track adoption status. States include: COMPLETED, FOLLOW_UP_PENDING, FOLLOW_UP_COMPLETED, RETURNED.
