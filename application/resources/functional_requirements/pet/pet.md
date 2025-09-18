# Pet Entity

## Description
Represents a pet available in the Purrfect Pets store.

## Attributes
- **name**: Pet's name (string, required)
- **category**: Pet category reference (string, required)
- **photo_urls**: List of photo URLs (array of strings)
- **tags**: List of tags for categorization (array of strings)
- **status**: Current availability status (mapped to entity.meta.state)

## Relationships
- **category**: References Category entity
- **orders**: Referenced by Order entities

## Notes
The pet's availability status (available/pending/sold) is managed through the workflow state system and should not appear in the entity schema.
