# Permission Entity

## Description
Represents specific access rights and capabilities within the system.

## Attributes
- **name**: Permission name (string, required, unique)
- **description**: Permission description (string, required)
- **resource**: Target resource/module (string, required)
- **action**: Allowed action (string, required)
- **is_active**: Permission status (boolean, default: true)
- **created_at**: Permission creation timestamp (datetime)

## Relationships
- **Many-to-Many with Role**: Permissions can be assigned to multiple roles

## Business Rules
- Permission names must be unique
- Resource and action combination should be unique
- Active permissions can be assigned to roles
- System permissions cannot be deleted
- Common actions: create, read, update, delete, manage
