# Pet Entity

## Description
Represents pets available in the Purrfect Pets store for adoption.

## Attributes
- **name**: Pet's name (string)
- **species**: Type of animal (string) - e.g., "cat", "dog", "bird"
- **breed**: Pet's breed (string)
- **age**: Pet's age in years (number)
- **description**: Pet's description and personality (string)
- **medical_history**: Medical background information (string)
- **adoption_fee**: Cost to adopt the pet (number)

## Relationships
- **owner_id**: Reference to Owner entity (nullable, set when adopted)
- **adoption_id**: Reference to Adoption entity (nullable, set during adoption process)

## Notes
- Entity state managed internally via `entity.meta.state`
- Available states: available, reserved, adopted
- Pet becomes reserved during adoption process, then adopted when completed
