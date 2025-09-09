# Criteria Requirements

## ExampleEntityValidationCriterion

### Description
The ExampleEntityValidationCriterion validates that an ExampleEntity meets all required business rules before it can proceed to the processing stage.

### Entity
ExampleEntity

### Validation Rules

#### 1. Required Fields Validation
- `name`: Must be non-empty string with minimum 3 characters and maximum 100 characters
- `description`: Must be non-empty string with maximum 500 characters
- `value`: Must be a positive number (greater than 0)
- `category`: Must be one of the allowed categories: "ELECTRONICS", "CLOTHING", "BOOKS", "HOME", "SPORTS"
- `isActive`: Must be a boolean value

#### 2. Business Logic Validation
- If `category` is "ELECTRONICS", `value` must be greater than 10
- If `category` is "CLOTHING", `value` must be between 5 and 1000
- If `category` is "BOOKS", `value` must be between 1 and 500
- If `isActive` is false, `value` must be less than 100

#### 3. Data Consistency Validation
- `createdAt` must be a valid ISO 8601 timestamp
- `updatedAt` must be greater than or equal to `createdAt`
- Entity must be in `created` state

### Validation Logic (Pseudocode)

```
validate(entity):
    // Check entity state
    if entity.meta.state != "created":
        return false
    
    // Validate required fields
    if is_empty(entity.name) or length(entity.name) < 3 or length(entity.name) > 100:
        return false
    
    if is_empty(entity.description) or length(entity.description) > 500:
        return false
    
    if entity.value <= 0:
        return false
    
    allowed_categories = ["ELECTRONICS", "CLOTHING", "BOOKS", "HOME", "SPORTS"]
    if entity.category not in allowed_categories:
        return false
    
    if typeof(entity.isActive) != "boolean":
        return false
    
    // Validate business logic rules
    if entity.category == "ELECTRONICS" and entity.value <= 10:
        return false
    
    if entity.category == "CLOTHING" and (entity.value < 5 or entity.value > 1000):
        return false
    
    if entity.category == "BOOKS" and (entity.value < 1 or entity.value > 500):
        return false
    
    if entity.isActive == false and entity.value >= 100:
        return false
    
    // Validate timestamps
    if not is_valid_iso8601(entity.createdAt):
        return false
    
    if not is_valid_iso8601(entity.updatedAt):
        return false
    
    if parse_timestamp(entity.updatedAt) < parse_timestamp(entity.createdAt):
        return false
    
    // All validations passed
    return true
```

### Return Value
- `true`: Entity passes all validation rules and can proceed to processing
- `false`: Entity fails one or more validation rules and cannot proceed

### Error Logging
The criterion should log validation failures for debugging purposes, but the actual return value should only be boolean.
