# Adoption Entity

## Description
Represents the adoption process linking pets with their new owners.

## Attributes
- **application_date**: When adoption was requested (string, ISO date)
- **adoption_date**: When adoption was completed (string, ISO date, nullable)
- **notes**: Additional notes about the adoption (string)
- **fee_paid**: Amount paid for adoption (number)
- **contract_signed**: Whether adoption contract is signed (boolean)

## Relationships
- **pet_id**: Reference to Pet being adopted (string)
- **owner_id**: Reference to adopting Owner (string)

## Notes
- Entity state managed internally via `entity.meta.state`
- Available states: pending, approved, completed, cancelled
- Links Pet and Owner entities during adoption process
