# Category Entity Requirements

## Entity: Category

**Purpose**: Represents pet categories for organization and filtering.

**Attributes**:
- `id`: Unique identifier (integer)
- `name`: Category name (string)

**Relationships**:
- Has many Pets

**Business Rules**:
- Category names should be descriptive
- Used for pet classification and filtering
- Simple reference entity with minimal workflow
