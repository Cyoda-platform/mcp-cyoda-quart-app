# HN Items Collection Controllers

## Overview
The HN Items Collection controller provides REST API endpoints for managing collections of multiple Hacker News items. It supports collection creation, population, validation, and management operations.

## Controller Name
**HnItemsCollectionController**

## Base URL
`/api/v1/hnitemscollection`

## Endpoints

### 1. Create HN Items Collection
**POST** `/api/v1/hnitemscollection`

Creates a new collection for HN items.

#### Request Body
```json
{
  "name": "Top Stories December 2023",
  "description": "Collection of top-rated stories from December 2023",
  "collection_type": "manual",
  "tags": ["top-stories", "december-2023"],
  "sort_order": "score",
  "transition": null
}
```

#### Response (201 Created)
```json
{
  "success": true,
  "data": {
    "technical_id": "collection_123456",
    "collection_id": "top_stories_dec_2023",
    "name": "Top Stories December 2023",
    "description": "Collection of top-rated stories from December 2023",
    "collection_type": "manual",
    "tags": ["top-stories", "december-2023"],
    "sort_order": "score",
    "total_items": 0,
    "item_count": 0,
    "status": "active",
    "created_at": 1640995200,
    "meta": {
      "state": "created",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z"
    }
  },
  "message": "HN Items Collection created successfully"
}
```

### 2. Get Collection by ID
**GET** `/api/v1/hnitemscollection/{technical_id}`

Retrieves a specific collection by its technical ID.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "collection_123456",
    "collection_id": "top_stories_dec_2023",
    "name": "Top Stories December 2023",
    "description": "Collection of top-rated stories from December 2023",
    "collection_type": "manual",
    "tags": ["top-stories", "december-2023"],
    "item_ids": [8863, 8864, 8865],
    "total_items": 3,
    "item_count": 3,
    "sort_order": "score",
    "status": "active",
    "created_by": "user123",
    "created_at": 1640995200,
    "updated_at": 1640995300,
    "meta": {
      "state": "ready",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:05:00Z"
    }
  }
}
```

### 3. Update Collection
**PUT** `/api/v1/hnitemscollection/{technical_id}`

Updates an existing collection and optionally triggers a workflow transition.

#### Request Body
```json
{
  "name": "Updated: Top Stories December 2023",
  "description": "Updated collection of top-rated stories",
  "tags": ["top-stories", "december-2023", "updated"],
  "transition": "start_population"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "collection_123456",
    "collection_id": "top_stories_dec_2023",
    "name": "Updated: Top Stories December 2023",
    "description": "Updated collection of top-rated stories",
    "tags": ["top-stories", "december-2023", "updated"],
    "meta": {
      "state": "populating",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:10:00Z"
    }
  },
  "message": "Collection updated and transition 'start_population' triggered"
}
```

### 4. List Collections
**GET** `/api/v1/hnitemscollection`

Retrieves a list of collections with optional filtering and pagination.

#### Query Parameters
- `collection_type` (optional): Filter by collection type
- `status` (optional): Filter by status (active, archived, processing)
- `state` (optional): Filter by workflow state
- `created_by` (optional): Filter by creator
- `tags` (optional): Filter by tags (comma-separated)
- `limit` (optional): Number of collections to return (default: 50, max: 200)
- `offset` (optional): Number of collections to skip (default: 0)
- `sort` (optional): Sort field (created_at, updated_at, name, item_count) (default: created_at)
- `order` (optional): Sort order (asc, desc) (default: desc)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "collections": [
      {
        "technical_id": "collection_123456",
        "collection_id": "top_stories_dec_2023",
        "name": "Top Stories December 2023",
        "collection_type": "manual",
        "item_count": 3,
        "status": "active",
        "created_at": 1640995200,
        "meta": {
          "state": "ready"
        }
      }
    ],
    "pagination": {
      "total": 25,
      "limit": 50,
      "offset": 0,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### 5. Add Items to Collection
**POST** `/api/v1/hnitemscollection/{technical_id}/items`

Adds HN items to a collection.

#### Request Body
```json
{
  "item_ids": [8866, 8867, 8868],
  "auto_validate": true
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "collection_id": "top_stories_dec_2023",
    "added_items": [8866, 8867, 8868],
    "total_items": 6,
    "item_count": 6,
    "summary": {
      "requested": 3,
      "added": 3,
      "skipped": 0,
      "failed": 0
    }
  },
  "message": "Items added to collection successfully"
}
```

### 6. Remove Items from Collection
**DELETE** `/api/v1/hnitemscollection/{technical_id}/items`

Removes HN items from a collection.

#### Request Body
```json
{
  "item_ids": [8866, 8867]
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "collection_id": "top_stories_dec_2023",
    "removed_items": [8866, 8867],
    "total_items": 4,
    "item_count": 4,
    "summary": {
      "requested": 2,
      "removed": 2,
      "not_found": 0
    }
  },
  "message": "Items removed from collection successfully"
}
```

### 7. Get Collection Items
**GET** `/api/v1/hnitemscollection/{technical_id}/items`

Retrieves items in a collection with optional filtering and pagination.

#### Query Parameters
- `type` (optional): Filter by item type
- `limit` (optional): Number of items to return (default: 50, max: 200)
- `offset` (optional): Number of items to skip (default: 0)
- `include_details` (optional): Include full item details (default: false)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "collection": {
      "technical_id": "collection_123456",
      "collection_id": "top_stories_dec_2023",
      "name": "Top Stories December 2023"
    },
    "items": [
      {
        "technical_id": "hn_item_123456",
        "id": 8863,
        "type": "story",
        "title": "My YC app: Dropbox",
        "score": 111,
        "by": "dhouston"
      }
    ],
    "pagination": {
      "total": 4,
      "limit": 50,
      "offset": 0,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### 8. Delete Collection
**DELETE** `/api/v1/hnitemscollection/{technical_id}`

Deletes a collection (soft delete - marks as archived).

#### Response (200 OK)
```json
{
  "success": true,
  "message": "Collection archived successfully"
}
```

### 9. Trigger Workflow Transition
**POST** `/api/v1/hnitemscollection/{technical_id}/transition`

Triggers a specific workflow transition for a collection.

#### Request Body
```json
{
  "transition": "validate_collection",
  "parameters": {
    "force_validation": true
  }
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "collection_123456",
    "previous_state": "populated",
    "current_state": "validating",
    "transition": "validate_collection",
    "triggered_at": "2023-12-01T10:15:00Z"
  },
  "message": "Transition 'validate_collection' triggered successfully"
}
```

### 10. Get Collection Statistics
**GET** `/api/v1/hnitemscollection/{technical_id}/stats`

Retrieves statistics for a collection.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "collection_id": "top_stories_dec_2023",
    "statistics": {
      "total_items": 4,
      "item_types": {
        "story": 3,
        "comment": 1
      },
      "score_stats": {
        "min": 45,
        "max": 111,
        "average": 78.5,
        "total": 314
      },
      "time_range": {
        "earliest": 1175714200,
        "latest": 1175814200
      },
      "authors": {
        "unique_count": 3,
        "top_contributors": [
          {"username": "dhouston", "items": 2},
          {"username": "commenter1", "items": 1}
        ]
      }
    },
    "generated_at": "2023-12-01T10:20:00Z"
  }
}
```

### 11. Export Collection
**GET** `/api/v1/hnitemscollection/{technical_id}/export`

Exports collection data in various formats.

#### Query Parameters
- `format` (optional): Export format (json, csv) (default: json)
- `include_items` (optional): Include full item data (default: true)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "collection": {
      "collection_id": "top_stories_dec_2023",
      "name": "Top Stories December 2023",
      "exported_at": "2023-12-01T10:25:00Z"
    },
    "items": [
      {
        "id": 8863,
        "type": "story",
        "by": "dhouston",
        "title": "My YC app: Dropbox",
        "score": 111
      }
    ],
    "export_info": {
      "format": "json",
      "total_items": 4,
      "file_size_bytes": 2048
    }
  }
}
```

## Workflow Transitions

The following transitions are available for collections:

1. **start_population**: Starts populating the collection with items
2. **validate_collection**: Validates the collection and its items
3. **archive_collection**: Archives the collection
4. **retry_processing**: Retries processing for failed collections

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      "Field 'name' is required",
      "Field 'collection_type' must be one of: manual, firebase_fetch, search_result, bulk_import"
    ]
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "COLLECTION_NOT_FOUND",
    "message": "Collection not found",
    "details": "No collection found with technical_id: collection_123456"
  }
}
```

### 409 Conflict
```json
{
  "success": false,
  "error": {
    "code": "COLLECTION_ALREADY_EXISTS",
    "message": "Collection with this ID already exists",
    "details": "Collection with ID 'top_stories_dec_2023' already exists"
  }
}
```
