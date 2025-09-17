# Search Query Entity

## Overview
The Search Query entity handles search operations for Hacker News items with support for complex queries, filtering, and parent hierarchy joins. It enables powerful search capabilities across the HN item database.

## Entity Name
- **Entity Name**: SearchQuery
- **Technical Name**: searchquery

## Attributes

### Required Attributes
- **query_id** (string): Unique identifier for the search query
- **query_text** (string): The search query text or criteria
- **query_type** (string): Type of search ("text", "field", "complex", "hierarchy")

### Optional Attributes
- **description** (string): Description of the search query
- **filters** (object): Filter criteria for the search
- **sort_criteria** (object): Sorting criteria for results
- **include_hierarchy** (boolean): Whether to include parent hierarchy in results
- **max_results** (integer): Maximum number of results to return
- **offset** (integer): Offset for pagination
- **search_fields** (array of strings): Specific fields to search in
- **date_range** (object): Date range filter with start and end timestamps
- **item_types** (array of strings): Filter by item types (story, comment, job, etc.)
- **score_range** (object): Score range filter with min and max values
- **author_filter** (string): Filter by specific author
- **executed_by** (string): Username who executed the search

### System Attributes
- **created_at** (integer): Unix timestamp when query was created
- **executed_at** (integer): Unix timestamp when query was last executed
- **execution_time** (integer): Query execution time in milliseconds
- **result_count** (integer): Number of results returned
- **result_collection_id** (string): ID of collection created with search results
- **cache_key** (string): Cache key for query results
- **cache_expires_at** (integer): Cache expiration timestamp

## Entity State Management
The entity state is managed internally via `entity.meta.state` and should NOT appear in the entity schema. The workflow manages the following states:
- **created**: Query has been created but not executed
- **validating**: Query syntax and parameters are being validated
- **executing**: Query is being executed against the database
- **completed**: Query execution completed successfully
- **cached**: Results are cached and available
- **failed**: Query execution failed

## Relationships

### Search Relationships
- **Searches HN Items**: Query searches across HN Item entities
- **Creates Collection**: Search results are stored in HN Items Collection
- **References Parent Items**: Hierarchy searches include parent-child relationships

### Result Relationships
- **Result Collection**: Links to collection containing search results
- **Cached Results**: Links to cached query results for performance

## Validation Rules
1. **Query ID Uniqueness**: Each query must have a unique `query_id`
2. **Query Text Required**: Query must have non-empty query text or criteria
3. **Type Validation**: `query_type` must be one of the allowed values
4. **Filter Validation**: Filter criteria must be valid JSON objects
5. **Field Validation**: Search fields must be valid HN Item attributes
6. **Range Validation**: Date and score ranges must have valid min/max values

## Business Rules
1. **Performance Limits**: Queries have execution time and result count limits
2. **Caching Strategy**: Frequently used queries are cached for performance
3. **Hierarchy Joins**: Parent hierarchy searches include full parent chain
4. **Permission Checks**: Users can only search items they have access to
5. **Result Pagination**: Large result sets are paginated automatically
6. **Query Optimization**: Complex queries are optimized for performance
7. **Audit Logging**: All search operations are logged for audit purposes
8. **Rate Limiting**: Search operations are rate-limited per user

## Query Types
- **text**: Full-text search across item content
- **field**: Search specific fields with exact or partial matches
- **complex**: Complex queries with multiple criteria and boolean logic
- **hierarchy**: Searches that include parent-child relationships

## Search Features
- **Full-text Search**: Search across title, text, and other content fields
- **Field-specific Search**: Search specific attributes like author, type, score
- **Range Queries**: Search within date ranges, score ranges, etc.
- **Boolean Logic**: Support AND, OR, NOT operations
- **Wildcard Search**: Support wildcard and regex patterns
- **Fuzzy Search**: Approximate string matching
- **Parent Hierarchy**: Include parent comments/stories in results
- **Child Hierarchy**: Include child comments in results

## Filter Criteria Structure
```json
{
  "filters": {
    "item_types": ["story", "comment"],
    "date_range": {
      "start": 1640995200,
      "end": 1672531200
    },
    "score_range": {
      "min": 10,
      "max": 1000
    },
    "author": "specific_user",
    "has_url": true,
    "has_children": true
  }
}
```

## Sort Criteria Structure
```json
{
  "sort_criteria": {
    "primary": {
      "field": "score",
      "direction": "desc"
    },
    "secondary": {
      "field": "time",
      "direction": "desc"
    }
  }
}
```
