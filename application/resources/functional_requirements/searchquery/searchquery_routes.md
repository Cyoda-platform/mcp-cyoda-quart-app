# SearchQuery Routes Requirements

## Base Route: `/searchquery`

## Endpoints

### POST /searchquery
Execute a search query
- **Body**: Search parameters and filters
- **Transition**: Optional transition name

**Request Example:**
```json
{
  "data": {
    "query_text": "dropbox startup",
    "filters": {
      "type": "story",
      "author": "dhouston",
      "date_range": {
        "start": "2024-01-01",
        "end": "2024-12-31"
      },
      "min_score": 10
    },
    "include_children": true,
    "parent_hierarchy": true,
    "sort_by": "relevance",
    "limit": 50,
    "offset": 0
  },
  "transition": "execute_search"
}
```

**Response Example:**
```json
{
  "id": "search-uuid",
  "results": [
    {
      "item_id": "hn-item-uuid",
      "relevance_score": 0.95,
      "data": {
        "id": 8863,
        "type": "story",
        "title": "My YC app: Dropbox",
        "score": 111
      }
    }
  ],
  "metadata": {
    "total_results": 25,
    "execution_time": "150ms",
    "cached": false
  }
}
```

### GET /searchquery/{id}
Get search query results and status

**Response Example:**
```json
{
  "id": "uuid",
  "data": {
    "query_text": "dropbox startup",
    "results_count": 25,
    "execution_time": "150ms"
  },
  "meta": {
    "state": "cached"
  }
}
```

### GET /searchquery/cached
Get cached search results by query hash

**Request Example:**
```
GET /searchquery/cached?query_hash=abc123&include_results=true
```
