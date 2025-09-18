# User Entity

## Description
Represents a customer in the Purrfect Pets store.

## Attributes
- **username**: Unique username (string, required)
- **first_name**: User's first name (string)
- **last_name**: User's last name (string)
- **email**: Email address (string, required)
- **phone**: Phone number (string)
- **address**: Physical address (string)

## Relationships
- **orders**: Referenced by Order entities

## Notes
User account status (registered/active/inactive) is managed through the workflow state system and should not appear in the entity schema.
