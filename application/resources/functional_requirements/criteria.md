# Criteria for Purrfect Pets API

## Overview
Criteria implement conditional logic for workflow transitions. They check if specific conditions are met before allowing a transition to proceed.

## Pet Criteria

### PetValidationCriterion
**Entity**: Pet
**Purpose**: Validate that a pet has all required information for activation
**Transition**: registered → active

**Validation Logic**:
- Pet name is not empty and contains only valid characters
- Species is from approved list (dog, cat, bird, fish, rabbit, hamster, etc.)
- Owner exists and is in active state
- Pet age is reasonable (0-30 years)
- Weight is positive if provided
- Microchip ID is unique if provided

**Returns**: true if all validations pass, false otherwise

## Owner Criteria

### OwnerContactValidationCriterion
**Entity**: Owner
**Purpose**: Validate that owner's contact information is correct and verified
**Transition**: registered → verified

**Validation Logic**:
- Email format is valid and email is deliverable
- Phone number format is valid for the region
- At least one contact method (email or phone) is verified
- Emergency contact information is provided if required
- Address information is complete if provided

**Returns**: true if contact validation passes, false otherwise

## Veterinarian Criteria

### VeterinarianLicenseValidationCriterion
**Entity**: Veterinarian
**Purpose**: Validate veterinarian's license and credentials
**Transition**: hired → licensed

**Validation Logic**:
- License number is valid format for the jurisdiction
- License is currently active and not expired
- License is not suspended or revoked
- Veterinarian's name matches license records
- Specialization credentials are valid if claimed
- No disciplinary actions that would prevent practice

**Returns**: true if license validation passes, false otherwise

## Appointment Criteria

### AppointmentValidationCriterion
**Entity**: Appointment
**Purpose**: Validate that an appointment can be confirmed
**Transition**: scheduled → confirmed

**Validation Logic**:
- Pet is in active state
- Owner is in active state
- Veterinarian is in active state and available
- Appointment date is in the future
- Appointment duration is reasonable (15-240 minutes)
- No scheduling conflicts exist
- Appointment type is valid
- Pet species matches veterinarian's expertise if specialized

**Returns**: true if appointment can be confirmed, false otherwise

## MedicalRecord Criteria

### MedicalRecordValidationCriterion
**Entity**: MedicalRecord
**Purpose**: Validate that a medical record is complete and accurate
**Transition**: draft → completed

**Validation Logic**:
- Pet exists and record belongs to correct pet
- Veterinarian exists and is authorized to create records
- Visit date is not in the future
- At least one of diagnosis, treatment, or notes is provided
- Medications are properly formatted if provided
- Cost is non-negative if provided
- Follow-up date is in the future if follow-up is required

**Returns**: true if medical record is valid for completion, false otherwise

## Additional Validation Rules

### General Validation Principles
All criteria should implement the following general principles:

1. **Data Integrity**: Ensure all referenced entities exist and are in valid states
2. **Business Rules**: Enforce business-specific rules (e.g., appointment duration limits)
3. **Security**: Verify permissions and authorization where applicable
4. **Consistency**: Maintain data consistency across related entities
5. **Compliance**: Ensure compliance with veterinary and data protection regulations

### Error Handling
When criteria return false, they should:
- Log the specific validation failure reason
- Provide clear error messages for debugging
- Not expose sensitive information in error messages
- Allow for retry after correction of validation issues

### Performance Considerations
Criteria should be designed to:
- Execute quickly to avoid workflow delays
- Cache validation results where appropriate
- Minimize database queries
- Use efficient validation algorithms

### Extensibility
Criteria should be designed to:
- Allow for easy addition of new validation rules
- Support configuration-based rule changes
- Enable different validation rules for different environments
- Support A/B testing of validation logic
