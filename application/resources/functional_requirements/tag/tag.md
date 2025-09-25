# Tag Entity Requirements

## Entity: Tag

**Purpose**: Represents tags for pet labeling and search functionality.

**Attributes**:
- `id`: Unique identifier (integer)
- `name`: Tag name (string)

**Relationships**:
- Associated with many Pets (many-to-many)

**Business Rules**:
- Tag names should be descriptive keywords
- Used for pet search and filtering
- Simple reference entity with minimal workflow
