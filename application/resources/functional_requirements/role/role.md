# Role Entity

## Description
Represents user roles that group permissions for access control.

## Attributes
- **name**: Role name (string, required, unique)
- **description**: Role description (string, required)
- **permission_ids**: Array of assigned permission IDs (array of strings)
- **is_active**: Role status (boolean, default: true)
- **created_at**: Role creation timestamp (datetime)
- **updated_at**: Last modification timestamp (datetime)

## Relationships
- **Many-to-Many with User**: Roles can be assigned to multiple users
- **Many-to-Many with Permission**: Roles can have multiple permissions

## Business Rules
- Role names must be unique
- Active roles can be assigned to users
- Inactive roles cannot be assigned but existing assignments remain
- System admin role cannot be deleted
