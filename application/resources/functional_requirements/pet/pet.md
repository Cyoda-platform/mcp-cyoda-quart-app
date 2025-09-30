# Pet Entity

## Description
Represents pets available for adoption or sale in the Purrfect Pets store.

## Attributes
- **name**: Pet's name (string)
- **species**: Type of animal (string) - dog, cat, bird, rabbit, etc.
- **breed**: Specific breed (string)
- **age**: Age in years (number)
- **color**: Pet's color/markings (string)
- **size**: Size category (string) - small, medium, large
- **price**: Adoption/sale price (number)
- **description**: Detailed description (string)
- **categoryId**: Reference to Category entity (string)
- **imageUrl**: Photo URL (string)
- **isAvailable**: Availability status (boolean)
- **healthStatus**: Health condition (string) - healthy, needs_care, vaccinated

## Relationships
- **Category**: Many-to-one relationship with Category entity
- **Order**: One-to-many relationship with Order entity (pets can be in multiple orders)

## Business Rules
- Pet state managed through entity.meta.state (not in schema)
- Available pets can be ordered
- Sold pets become unavailable
