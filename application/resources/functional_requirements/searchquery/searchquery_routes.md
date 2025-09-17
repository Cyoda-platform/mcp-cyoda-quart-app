# SearchQuery Routes

## Base Route: `/searchquery`

### POST /searchquery
Execute search query
- **Body**: Search parameters
- **Transition**: validate_query (optional)

**Request Example**:
```json
{
  "query_text": "dropbox startup",
  "filters": {
    "type": "story",
    "by": "dhouston",
    "score_min": 10,
    "date_from": "2023-01-01"
  },
  "include_hierarchy": true,
  "sort_order": "score_desc",
  "limit": 20,
  "offset": 0
}
```

**Response Example**:
```json
{
  "query_id": "generated-uuid",
  "result_count": 15,
  "execution_time_ms": 45,
  "results": [
    {
      "id": 8863,
      "type": "story",
      "title": "My YC app: Dropbox",
      "score": 111,
      "parent_chain": []
    }
  ]
}
```

### GET /searchquery/{id}
Get search query results by ID

### POST /searchquery/hierarchy
Search with parent hierarchy expansion
- **Body**: Search parameters with hierarchy options

**Request Example**:
```json
{
  "query_text": "interesting comment",
  "filters": {"type": "comment"},
  "include_hierarchy": true,
  "hierarchy_depth": 3
}
```

### GET /searchquery/suggestions
Get search suggestions based on query text
- **Query params**: q (partial query text)

**Request Example**:
```
GET /searchquery/suggestions?q=drop
```

**Response Example**:
```json
{
  "suggestions": ["dropbox", "dropdown", "drop table"]
}
```
