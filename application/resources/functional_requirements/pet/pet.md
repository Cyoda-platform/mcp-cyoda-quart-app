# Pet Entity

## Description
Represents a pet retrieved from the external Petstore API with transformed data for user-friendly display.

## Attributes
- **name**: Pet's display name (transformed from "petName")
- **species**: Pet species (e.g., "dog", "cat")
- **status**: Pet availability status (e.g., "available", "pending", "sold")
- **categoryId**: Category identifier for pet classification
- **categoryName**: Human-readable category name
- **availabilityStatus**: User-friendly availability description
- **photoUrls**: Array of pet photo URLs
- **tags**: Array of pet tags for additional classification

## Relationships
- Related to Search entity through search results
- No direct entity relationships (external API data)

## Notes
- Entity state managed internally via `entity.meta.state`
- Data sourced from external Petstore API
- Transformation applied during ingestion process
