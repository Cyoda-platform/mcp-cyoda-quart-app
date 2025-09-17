# SearchQuery Entity

## Description
Handles search functionality for HN items with support for complex queries and parent hierarchy joins.

## Attributes
- **query_id**: Unique identifier for the search query
- **query_text**: Text search terms
- **filters**: Search filters (type, author, date range, etc.)
- **include_hierarchy**: Boolean to include parent hierarchy in results
- **sort_order**: Sort criteria (score, time, relevance)
- **limit**: Maximum number of results
- **offset**: Pagination offset
- **executed_at**: Query execution timestamp
- **execution_time_ms**: Query execution time
- **result_count**: Number of results found
- **results**: Array of matching HNItem references

## Relationships
- References multiple HNItem entities in results
- Can traverse HNItem parent-child relationships

## State Management
Entity state managed internally via `entity.meta.state` - not exposed in schema.
