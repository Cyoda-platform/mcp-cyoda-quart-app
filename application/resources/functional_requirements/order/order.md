# Order Entity

## Description
Represents a pet purchase order in the Purrfect Pets store.

## Attributes
- **pet_id**: Reference to the pet being ordered (string, required)
- **user_id**: Reference to the user placing the order (string, required)
- **quantity**: Number of pets ordered (integer, default: 1)
- **ship_date**: Expected shipping date (string, ISO date)
- **total_amount**: Total order amount (number)

## Relationships
- **pet_id**: References Pet entity
- **user_id**: References User entity

## Notes
Order status (placed/approved/delivered) is managed through the workflow state system and should not appear in the entity schema.
