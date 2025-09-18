# Category Entity

## Description
Represents a pet category for organizing pets in the Purrfect Pets store.

## Attributes
- **name**: Category name (string, required)
- **description**: Category description (string)

## Relationships
- **pets**: Referenced by Pet entities

## Notes
Category status (draft/active/archived) is managed through the workflow state system and should not appear in the entity schema.
