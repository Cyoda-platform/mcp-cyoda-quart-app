# Search Query Controllers

## Overview
The Search Query controller provides REST API endpoints for executing search operations on Hacker News items with support for complex queries, filtering, and parent hierarchy joins.

## Controller Name
**SearchQueryController**

## Base URL
`/api/v1/searchquery`

## Endpoints

### 1. Create Search Query
**POST** `/api/v1/searchquery`

Creates and executes a new search query.

#### Request Body
```json
{
  "query_text": "dropbox file sharing",
  "query_type": "text",
  "description": "Search for Dropbox-related stories",
  "filters": {
    "item_types": ["story"],
    "date_range": {
      "start": 1640995200,
      "end": 1672531200
    },
    "score_range": {
      "min": 10,
      "max": 1000
    }
  },
  "sort_criteria": {
    "primary": {
      "field": "score",
      "direction": "desc"
    }
  },
  "include_hierarchy": true,
  "max_results": 100,
  "transition": "validate_query"
}
```

#### Response (201 Created)
```json
{
  "success": true,
  "data": {
    "technical_id": "query_123456",
    "query_id": "search_dropbox_20231201",
    "query_text": "dropbox file sharing",
    "query_type": "text",
    "description": "Search for Dropbox-related stories",
    "filters": {
      "item_types": ["story"],
      "date_range": {
        "start": 1640995200,
        "end": 1672531200
      },
      "score_range": {
        "min": 10,
        "max": 1000
      }
    },
    "include_hierarchy": true,
    "max_results": 100,
    "created_at": 1640995200,
    "meta": {
      "state": "validating",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z"
    }
  },
  "message": "Search query created and validation started"
}
```

### 2. Execute Search Query
**POST** `/api/v1/searchquery/execute`

Executes a search query directly without creating a persistent query record.

#### Request Body
```json
{
  "query_text": "YC startup",
  "query_type": "text",
  "filters": {
    "item_types": ["story"],
    "score_range": {
      "min": 50
    }
  },
  "max_results": 50,
  "include_hierarchy": false
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "query_info": {
      "query_text": "YC startup",
      "query_type": "text",
      "executed_at": "2023-12-01T10:05:00Z",
      "execution_time_ms": 250
    },
    "results": [
      {
        "technical_id": "hn_item_123456",
        "id": 8863,
        "type": "story",
        "title": "My YC app: Dropbox - Throw away your USB drive",
        "by": "dhouston",
        "score": 111,
        "time": 1175714200,
        "relevance_score": 0.95
      }
    ],
    "result_stats": {
      "total_results": 25,
      "returned_results": 25,
      "execution_time_ms": 250,
      "cache_hit": false
    }
  },
  "message": "Search executed successfully"
}
```

### 3. Get Search Query by ID
**GET** `/api/v1/searchquery/{technical_id}`

Retrieves a specific search query by its technical ID.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "query_123456",
    "query_id": "search_dropbox_20231201",
    "query_text": "dropbox file sharing",
    "query_type": "text",
    "description": "Search for Dropbox-related stories",
    "filters": {
      "item_types": ["story"],
      "date_range": {
        "start": 1640995200,
        "end": 1672531200
      }
    },
    "result_count": 25,
    "result_collection_id": "search_results_001",
    "execution_time": 250,
    "executed_at": 1640995250,
    "executed_by": "user123",
    "cache_key": "search_cache_abc123",
    "cache_expires_at": 1640998850,
    "meta": {
      "state": "completed",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:05:00Z"
    }
  }
}
```

### 4. Get Search Results
**GET** `/api/v1/searchquery/{technical_id}/results`

Retrieves the results of a completed search query.

#### Query Parameters
- `limit` (optional): Number of results to return (default: 50, max: 200)
- `offset` (optional): Number of results to skip (default: 0)
- `include_hierarchy` (optional): Include parent hierarchy (default: false)
- `format` (optional): Response format (json, summary) (default: json)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "query_info": {
      "query_id": "search_dropbox_20231201",
      "query_text": "dropbox file sharing",
      "executed_at": "2023-12-01T10:05:00Z"
    },
    "results": [
      {
        "technical_id": "hn_item_123456",
        "id": 8863,
        "type": "story",
        "title": "My YC app: Dropbox - Throw away your USB drive",
        "by": "dhouston",
        "score": 111,
        "time": 1175714200,
        "url": "http://www.getdropbox.com/u/2/screencast.html",
        "relevance_score": 0.95,
        "hierarchy": {
          "parents": [],
          "children_count": 5
        }
      }
    ],
    "pagination": {
      "total": 25,
      "limit": 50,
      "offset": 0,
      "has_next": false,
      "has_prev": false
    },
    "result_stats": {
      "total_results": 25,
      "execution_time_ms": 250,
      "cache_hit": true
    }
  }
}
```

### 5. List Search Queries
**GET** `/api/v1/searchquery`

Retrieves a list of search queries with optional filtering and pagination.

#### Query Parameters
- `query_type` (optional): Filter by query type
- `state` (optional): Filter by workflow state
- `executed_by` (optional): Filter by executor
- `date_from` (optional): Filter by creation date (from)
- `date_to` (optional): Filter by creation date (to)
- `limit` (optional): Number of queries to return (default: 50, max: 200)
- `offset` (optional): Number of queries to skip (default: 0)
- `sort` (optional): Sort field (created_at, executed_at, result_count) (default: created_at)
- `order` (optional): Sort order (asc, desc) (default: desc)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "queries": [
      {
        "technical_id": "query_123456",
        "query_id": "search_dropbox_20231201",
        "query_text": "dropbox file sharing",
        "query_type": "text",
        "result_count": 25,
        "execution_time": 250,
        "executed_at": 1640995250,
        "meta": {
          "state": "completed"
        }
      }
    ],
    "pagination": {
      "total": 15,
      "limit": 50,
      "offset": 0,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### 6. Update Search Query
**PUT** `/api/v1/searchquery/{technical_id}`

Updates an existing search query and optionally re-executes it.

#### Request Body
```json
{
  "description": "Updated: Search for Dropbox-related stories",
  "max_results": 150,
  "transition": "validate_query"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "query_123456",
    "query_id": "search_dropbox_20231201",
    "description": "Updated: Search for Dropbox-related stories",
    "max_results": 150,
    "meta": {
      "state": "validating",
      "updated_at": "2023-12-01T10:15:00Z"
    }
  },
  "message": "Search query updated and re-validation started"
}
```

### 7. Trigger Workflow Transition
**POST** `/api/v1/searchquery/{technical_id}/transition`

Triggers a specific workflow transition for a search query.

#### Request Body
```json
{
  "transition": "validate_query",
  "parameters": {
    "force_execution": true
  }
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "query_123456",
    "previous_state": "created",
    "current_state": "validating",
    "transition": "validate_query",
    "triggered_at": "2023-12-01T10:20:00Z"
  },
  "message": "Transition 'validate_query' triggered successfully"
}
```

### 8. Get Search Suggestions
**GET** `/api/v1/searchquery/suggestions`

Gets search suggestions based on query text and historical searches.

#### Query Parameters
- `q` (required): Partial query text
- `limit` (optional): Number of suggestions (default: 10, max: 20)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "query": "dropb",
    "suggestions": [
      {
        "text": "dropbox",
        "type": "term",
        "frequency": 45,
        "relevance": 0.95
      },
      {
        "text": "dropbox file sharing",
        "type": "phrase",
        "frequency": 12,
        "relevance": 0.87
      }
    ],
    "popular_queries": [
      {
        "query_text": "YC startup",
        "usage_count": 156
      }
    ]
  }
}
```

### 9. Export Search Results
**GET** `/api/v1/searchquery/{technical_id}/export`

Exports search results in various formats.

#### Query Parameters
- `format` (optional): Export format (json, csv) (default: json)
- `include_hierarchy` (optional): Include hierarchy data (default: false)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "query_info": {
      "query_id": "search_dropbox_20231201",
      "exported_at": "2023-12-01T10:25:00Z"
    },
    "results": [
      {
        "id": 8863,
        "type": "story",
        "title": "My YC app: Dropbox",
        "by": "dhouston",
        "score": 111
      }
    ],
    "export_info": {
      "format": "json",
      "total_results": 25,
      "file_size_bytes": 15360
    }
  }
}
```

### 10. Delete Search Query
**DELETE** `/api/v1/searchquery/{technical_id}`

Deletes a search query and its cached results.

#### Response (200 OK)
```json
{
  "success": true,
  "message": "Search query deleted successfully"
}
```

### 11. Advanced Search
**POST** `/api/v1/searchquery/advanced`

Executes an advanced search with complex criteria and boolean logic.

#### Request Body
```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"title": "startup"}},
        {"range": {"score": {"gte": 50}}}
      ],
      "should": [
        {"match": {"text": "YC"}},
        {"match": {"by": "pg"}}
      ],
      "must_not": [
        {"match": {"title": "spam"}}
      ]
    }
  },
  "filters": {
    "item_types": ["story", "comment"],
    "date_range": {
      "start": 1640995200,
      "end": 1672531200
    }
  },
  "include_hierarchy": true,
  "max_results": 100
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "query_info": {
      "query_type": "advanced",
      "executed_at": "2023-12-01T10:30:00Z",
      "execution_time_ms": 450
    },
    "results": [
      {
        "technical_id": "hn_item_123456",
        "id": 8863,
        "type": "story",
        "title": "My YC app: Dropbox",
        "score": 111,
        "relevance_score": 0.92,
        "match_reasons": ["title_match", "score_threshold"]
      }
    ],
    "result_stats": {
      "total_results": 42,
      "execution_time_ms": 450,
      "query_complexity": "high"
    }
  }
}
```

## Workflow Transitions

The following transitions are available for search queries:

1. **validate_query**: Validates the query syntax and parameters
2. **cache_results**: Caches the search results for future use
3. **retry_query**: Retries a failed query execution

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "INVALID_QUERY",
    "message": "Invalid search query",
    "details": [
      "Query text cannot be empty",
      "Invalid query type: 'invalid_type'"
    ]
  }
}
```

### 422 Unprocessable Entity
```json
{
  "success": false,
  "error": {
    "code": "QUERY_EXECUTION_FAILED",
    "message": "Query execution failed",
    "details": "Syntax error in advanced query: unexpected token 'invalid'"
  }
}
```

### 429 Too Many Requests
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Search rate limit exceeded",
    "details": "Maximum 100 searches per hour exceeded. Try again in 30 minutes."
  }
}
```
