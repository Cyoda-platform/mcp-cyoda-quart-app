# User Entity

## Description
Represents customers who can adopt or purchase pets from the Purrfect Pets store.

## Attributes
- **firstName**: User's first name (string)
- **lastName**: User's last name (string)
- **email**: Email address (string)
- **phone**: Phone number (string)
- **address**: Home address (string)
- **city**: City (string)
- **zipCode**: Postal code (string)
- **dateOfBirth**: Birth date (string)
- **preferredPetType**: Preferred pet species (string)
- **experienceLevel**: Pet ownership experience (string) - beginner, intermediate, expert
- **livingSpace**: Type of living space (string) - apartment, house, farm

## Relationships
- **Order**: One-to-many relationship with Order entity

## Business Rules
- User state managed through entity.meta.state (not in schema)
- Users must be verified before placing orders
- Users can have multiple orders
