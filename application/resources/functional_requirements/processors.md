# Processors for Purrfect Pets API

## Overview
Processors implement the business logic for workflow transitions. Each processor modifies entity state or interacts with other entities.

## Pet Processors

### PetRegistrationProcessor
**Entity**: Pet
**Input**: Pet entity with basic information
**Purpose**: Register a new pet in the system
**Output**: Pet entity with registration_date set and initial validation

**Pseudocode**:
```
process(pet_entity):
    validate_required_fields(pet_entity.name, pet_entity.species, pet_entity.owner_id)
    verify_owner_exists(pet_entity.owner_id)
    set pet_entity.registration_date = current_timestamp()
    set pet_entity.is_active = true
    generate_unique_pet_id()
    log_registration_event()
    return pet_entity
```

### PetActivationProcessor
**Entity**: Pet
**Input**: Registered pet entity
**Purpose**: Activate a pet for appointments and services
**Output**: Pet entity ready for appointments

**Pseudocode**:
```
process(pet_entity):
    verify_owner_is_active(pet_entity.owner_id)
    set pet_entity.is_active = true
    create_welcome_notification(pet_entity.owner_id)
    log_activation_event()
    return pet_entity
```

### PetDeactivationProcessor
**Entity**: Pet
**Input**: Active pet entity
**Purpose**: Temporarily deactivate a pet
**Output**: Pet entity marked as inactive

**Pseudocode**:
```
process(pet_entity):
    cancel_future_appointments(pet_entity.pet_id)
    set pet_entity.is_active = false
    notify_owner_of_deactivation(pet_entity.owner_id)
    log_deactivation_event()
    return pet_entity
```

### PetReactivationProcessor
**Entity**: Pet
**Input**: Inactive pet entity
**Purpose**: Reactivate a previously deactivated pet
**Output**: Pet entity marked as active again

**Pseudocode**:
```
process(pet_entity):
    verify_owner_is_still_active(pet_entity.owner_id)
    set pet_entity.is_active = true
    notify_owner_of_reactivation(pet_entity.owner_id)
    log_reactivation_event()
    return pet_entity
```

### PetArchivalProcessor
**Entity**: Pet
**Input**: Pet entity (active or inactive)
**Purpose**: Permanently archive a pet record
**Output**: Pet entity marked as archived

**Pseudocode**:
```
process(pet_entity):
    cancel_all_future_appointments(pet_entity.pet_id)
    archive_medical_records(pet_entity.pet_id) // Transition: null
    set pet_entity.is_active = false
    create_archival_record()
    notify_owner_of_archival(pet_entity.owner_id)
    log_archival_event()
    return pet_entity
```

## Owner Processors

### OwnerRegistrationProcessor
**Entity**: Owner
**Input**: Owner entity with basic contact information
**Purpose**: Register a new pet owner
**Output**: Owner entity with registration details

**Pseudocode**:
```
process(owner_entity):
    validate_required_fields(owner_entity.first_name, owner_entity.last_name, owner_entity.email, owner_entity.phone)
    validate_email_format(owner_entity.email)
    check_duplicate_email(owner_entity.email)
    set owner_entity.registration_date = current_timestamp()
    generate_unique_owner_id()
    log_registration_event()
    return owner_entity
```

### OwnerVerificationProcessor
**Entity**: Owner
**Input**: Registered owner entity
**Purpose**: Verify owner's contact information
**Output**: Owner entity with verified status

**Pseudocode**:
```
process(owner_entity):
    send_verification_email(owner_entity.email)
    send_verification_sms(owner_entity.phone)
    create_verification_tokens()
    set_verification_expiry()
    log_verification_attempt()
    return owner_entity
```

### OwnerActivationProcessor
**Entity**: Owner
**Input**: Verified owner entity
**Purpose**: Activate owner for full system access
**Output**: Owner entity ready to schedule appointments

**Pseudocode**:
```
process(owner_entity):
    grant_appointment_permissions()
    send_welcome_email(owner_entity.email)
    create_owner_dashboard_access()
    log_activation_event()
    return owner_entity
```

### OwnerSuspensionProcessor
**Entity**: Owner
**Input**: Active owner entity
**Purpose**: Temporarily suspend an owner
**Output**: Owner entity marked as suspended

**Pseudocode**:
```
process(owner_entity):
    cancel_future_appointments(owner_entity.owner_id)
    deactivate_pets(owner_entity.owner_id) // Transition: "deactivate"
    revoke_system_access()
    notify_owner_of_suspension(owner_entity.email)
    log_suspension_event()
    return owner_entity
```

### OwnerReactivationProcessor
**Entity**: Owner
**Input**: Suspended owner entity
**Purpose**: Reactivate a suspended owner
**Output**: Owner entity restored to active status

**Pseudocode**:
```
process(owner_entity):
    restore_system_access()
    reactivate_pets(owner_entity.owner_id) // Transition: "reactivate"
    send_reactivation_notification(owner_entity.email)
    log_reactivation_event()
    return owner_entity
```

### OwnerArchivalProcessor
**Entity**: Owner
**Input**: Active owner entity
**Purpose**: Permanently archive an owner record
**Output**: Owner entity marked as archived

**Pseudocode**:
```
process(owner_entity):
    archive_all_pets(owner_entity.owner_id) // Transition: "archive"
    cancel_all_appointments(owner_entity.owner_id)
    archive_medical_records(owner_entity.owner_id) // Transition: null
    revoke_all_access()
    create_archival_record()
    log_archival_event()
    return owner_entity
```

## Veterinarian Processors

### VeterinarianHiringProcessor
**Entity**: Veterinarian
**Input**: Veterinarian entity with basic information
**Purpose**: Process hiring of a new veterinarian
**Output**: Veterinarian entity with hire details

**Pseudocode**:
```
process(vet_entity):
    validate_required_fields(vet_entity.first_name, vet_entity.last_name, vet_entity.license_number)
    check_duplicate_license(vet_entity.license_number)
    set vet_entity.hire_date = current_timestamp()
    set vet_entity.is_available = false
    generate_unique_vet_id()
    create_employee_record()
    log_hiring_event()
    return vet_entity
```

### VeterinarianLicenseVerificationProcessor
**Entity**: Veterinarian
**Input**: Hired veterinarian entity
**Purpose**: Verify veterinary license
**Output**: Veterinarian entity with verified license

**Pseudocode**:
```
process(vet_entity):
    verify_license_with_authority(vet_entity.license_number)
    check_license_expiry()
    validate_specialization_credentials()
    update_license_verification_status()
    log_verification_event()
    return vet_entity
```

### VeterinarianActivationProcessor
**Entity**: Veterinarian
**Input**: Licensed veterinarian entity
**Purpose**: Activate veterinarian for appointments
**Output**: Veterinarian entity ready to see patients

**Pseudocode**:
```
process(vet_entity):
    set vet_entity.is_available = true
    create_appointment_schedule()
    grant_system_access()
    send_welcome_email(vet_entity.email)
    log_activation_event()
    return vet_entity
```

### VeterinarianUnavailabilityProcessor
**Entity**: Veterinarian
**Input**: Active veterinarian entity
**Purpose**: Mark veterinarian as temporarily unavailable
**Output**: Veterinarian entity marked as unavailable

**Pseudocode**:
```
process(vet_entity):
    set vet_entity.is_available = false
    reschedule_future_appointments(vet_entity.vet_id)
    notify_affected_owners()
    update_schedule_availability()
    log_unavailability_event()
    return vet_entity
```

### VeterinarianAvailabilityProcessor
**Entity**: Veterinarian
**Input**: Unavailable veterinarian entity
**Purpose**: Mark veterinarian as available again
**Output**: Veterinarian entity marked as available

**Pseudocode**:
```
process(vet_entity):
    set vet_entity.is_available = true
    restore_appointment_schedule()
    notify_scheduling_system()
    log_availability_event()
    return vet_entity
```

### VeterinarianTerminationProcessor
**Entity**: Veterinarian
**Input**: Active veterinarian entity
**Purpose**: Process termination of veterinarian
**Output**: Veterinarian entity marked as terminated

**Pseudocode**:
```
process(vet_entity):
    set vet_entity.is_available = false
    reassign_future_appointments(vet_entity.vet_id)
    revoke_system_access()
    archive_medical_records(vet_entity.vet_id) // Transition: null
    create_termination_record()
    log_termination_event()
    return vet_entity
```
