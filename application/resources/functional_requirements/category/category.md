# Category Entity

## Description
Represents categories for organizing pets in the Purrfect Pets store.

## Attributes
- **name**: Category name (string) - Dogs, Cats, Birds, Rabbits, etc.
- **description**: Category description (string)
- **imageUrl**: Category image URL (string)
- **isActive**: Whether category is active (boolean)

## Relationships
- **Pet**: One-to-many relationship with Pet entity

## Business Rules
- Category state managed through entity.meta.state (not in schema)
- Categories can be activated/deactivated
- Inactive categories hide associated pets
