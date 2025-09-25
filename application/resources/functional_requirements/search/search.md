# Search Entity

## Description
Manages user search parameters and coordinates pet data retrieval with filtering criteria.

## Attributes
- **species**: Target pet species filter (e.g., "dog", "cat")
- **status**: Pet status filter (e.g., "available", "pending", "sold")
- **categoryId**: Category ID filter for pet classification
- **searchTimestamp**: When the search was initiated
- **resultCount**: Number of pets found matching criteria
- **hasResults**: Boolean indicating if search returned results

## Relationships
- Triggers Pet entity creation through search results
- No direct entity relationships (coordinates external API calls)

## Notes
- Entity state managed internally via `entity.meta.state`
- Triggers data ingestion and transformation processes
- Handles notification logic for empty results
