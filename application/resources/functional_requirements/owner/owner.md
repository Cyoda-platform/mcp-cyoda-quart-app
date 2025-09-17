# Owner Entity

## Description
Represents individuals who can adopt pets from the Purrfect Pets store.

## Attributes
- **name**: Owner's full name (string)
- **email**: Contact email address (string)
- **phone**: Phone number (string)
- **address**: Home address (string)
- **experience**: Pet ownership experience level (string) - e.g., "beginner", "experienced"
- **preferences**: Preferred pet types and characteristics (string)
- **verification_documents**: Uploaded verification files (string)

## Relationships
- **pet_ids**: List of adopted pet references (array of strings)
- **adoption_ids**: List of adoption process references (array of strings)

## Notes
- Entity state managed internally via `entity.meta.state`
- Available states: registered, verified, active
- Owner must be verified before adopting pets
