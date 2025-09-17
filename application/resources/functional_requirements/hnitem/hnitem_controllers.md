# HN Item Controllers

## Overview
The HN Item controller provides REST API endpoints for managing individual Hacker News items. It supports CRUD operations, workflow transitions, and Firebase HN API integration.

## Controller Name
**HnItemController**

## Base URL
`/api/v1/hnitem`

## Endpoints

### 1. Create HN Item
**POST** `/api/v1/hnitem`

Creates a new HN item from manual input or Firebase API data.

#### Request Body
```json
{
  "id": 8863,
  "type": "story",
  "by": "dhouston",
  "time": 1175714200,
  "title": "My YC app: Dropbox - Throw away your USB drive",
  "url": "http://www.getdropbox.com/u/2/screencast.html",
  "score": 111,
  "descendants": 71,
  "kids": [8952, 9224, 8917, 8884, 8887],
  "source": "manual_post",
  "transition": null
}
```

#### Response (201 Created)
```json
{
  "success": true,
  "data": {
    "technical_id": "hn_item_123456",
    "id": 8863,
    "type": "story",
    "by": "dhouston",
    "time": 1175714200,
    "title": "My YC app: Dropbox - Throw away your USB drive",
    "url": "http://www.getdropbox.com/u/2/screencast.html",
    "score": 111,
    "descendants": 71,
    "kids": [8952, 9224, 8917, 8884, 8887],
    "source": "manual_post",
    "imported_at": 1640995200,
    "meta": {
      "state": "pending",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z"
    }
  },
  "message": "HN item created successfully"
}
```

### 2. Get HN Item by ID
**GET** `/api/v1/hnitem/{technical_id}`

Retrieves a specific HN item by its technical ID.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "hn_item_123456",
    "id": 8863,
    "type": "story",
    "by": "dhouston",
    "time": 1175714200,
    "title": "My YC app: Dropbox - Throw away your USB drive",
    "url": "http://www.getdropbox.com/u/2/screencast.html",
    "score": 111,
    "descendants": 71,
    "kids": [8952, 9224, 8917, 8884, 8887],
    "source": "manual_post",
    "imported_at": 1640995200,
    "last_updated": 1640995200,
    "validation_status": "passed",
    "storage_status": "success",
    "meta": {
      "state": "stored",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:05:00Z"
    }
  }
}
```

### 3. Get HN Item by HN ID
**GET** `/api/v1/hnitem/hn/{hn_id}`

Retrieves a specific HN item by its original Hacker News ID.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "hn_item_123456",
    "id": 8863,
    "type": "story",
    "by": "dhouston",
    "time": 1175714200,
    "title": "My YC app: Dropbox - Throw away your USB drive",
    "url": "http://www.getdropbox.com/u/2/screencast.html",
    "score": 111,
    "descendants": 71,
    "kids": [8952, 9224, 8917, 8884, 8887],
    "source": "firebase_api",
    "imported_at": 1640995200,
    "meta": {
      "state": "stored",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:05:00Z"
    }
  }
}
```

### 4. Update HN Item
**PUT** `/api/v1/hnitem/{technical_id}`

Updates an existing HN item and optionally triggers a workflow transition.

#### Request Body
```json
{
  "title": "Updated: My YC app: Dropbox - Throw away your USB drive",
  "score": 115,
  "descendants": 75,
  "last_updated": 1640995300,
  "transition": "validate_item"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "hn_item_123456",
    "id": 8863,
    "type": "story",
    "by": "dhouston",
    "time": 1175714200,
    "title": "Updated: My YC app: Dropbox - Throw away your USB drive",
    "url": "http://www.getdropbox.com/u/2/screencast.html",
    "score": 115,
    "descendants": 75,
    "kids": [8952, 9224, 8917, 8884, 8887],
    "source": "manual_post",
    "imported_at": 1640995200,
    "last_updated": 1640995300,
    "meta": {
      "state": "validating",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:10:00Z"
    }
  },
  "message": "HN item updated and transition 'validate_item' triggered"
}
```

### 5. List HN Items
**GET** `/api/v1/hnitem`

Retrieves a list of HN items with optional filtering and pagination.

#### Query Parameters
- `type` (optional): Filter by item type (story, comment, job, poll, pollopt)
- `by` (optional): Filter by author username
- `source` (optional): Filter by source (firebase_api, manual_post, bulk_upload)
- `state` (optional): Filter by workflow state
- `limit` (optional): Number of items to return (default: 50, max: 200)
- `offset` (optional): Number of items to skip (default: 0)
- `sort` (optional): Sort field (time, score, id) (default: time)
- `order` (optional): Sort order (asc, desc) (default: desc)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "technical_id": "hn_item_123456",
        "id": 8863,
        "type": "story",
        "by": "dhouston",
        "time": 1175714200,
        "title": "My YC app: Dropbox - Throw away your USB drive",
        "score": 111,
        "source": "firebase_api",
        "meta": {
          "state": "stored",
          "created_at": "2023-12-01T10:00:00Z"
        }
      }
    ],
    "pagination": {
      "total": 1250,
      "limit": 50,
      "offset": 0,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 6. Delete HN Item
**DELETE** `/api/v1/hnitem/{technical_id}`

Deletes an HN item (soft delete - marks as deleted).

#### Response (200 OK)
```json
{
  "success": true,
  "message": "HN item deleted successfully"
}
```

### 7. Trigger Workflow Transition
**POST** `/api/v1/hnitem/{technical_id}/transition`

Triggers a specific workflow transition for an HN item.

#### Request Body
```json
{
  "transition": "validate_item",
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
    "technical_id": "hn_item_123456",
    "previous_state": "pending",
    "current_state": "validating",
    "transition": "validate_item",
    "triggered_at": "2023-12-01T10:15:00Z"
  },
  "message": "Transition 'validate_item' triggered successfully"
}
```

### 8. Get Item Hierarchy
**GET** `/api/v1/hnitem/{technical_id}/hierarchy`

Retrieves the parent-child hierarchy for an HN item.

#### Query Parameters
- `include_parents` (optional): Include parent items (default: true)
- `include_children` (optional): Include child items (default: true)
- `max_depth` (optional): Maximum depth for hierarchy (default: 5)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "item": {
      "technical_id": "hn_item_123456",
      "id": 8863,
      "type": "story",
      "title": "My YC app: Dropbox - Throw away your USB drive"
    },
    "parents": [],
    "children": [
      {
        "technical_id": "hn_item_789012",
        "id": 8952,
        "type": "comment",
        "by": "commenter1",
        "text": "Great idea! This could revolutionize file sharing.",
        "parent": 8863
      }
    ],
    "hierarchy_stats": {
      "total_parents": 0,
      "total_children": 5,
      "max_depth": 3
    }
  }
}
```

### 9. Bulk Create HN Items
**POST** `/api/v1/hnitem/bulk`

Creates multiple HN items in a single request.

#### Request Body
```json
{
  "items": [
    {
      "id": 8863,
      "type": "story",
      "by": "dhouston",
      "title": "My YC app: Dropbox",
      "source": "firebase_api"
    },
    {
      "id": 8864,
      "type": "comment",
      "by": "commenter1",
      "parent": 8863,
      "text": "Great idea!",
      "source": "firebase_api"
    }
  ],
  "auto_validate": true
}
```

#### Response (201 Created)
```json
{
  "success": true,
  "data": {
    "created_items": [
      {
        "technical_id": "hn_item_123456",
        "id": 8863,
        "status": "created"
      },
      {
        "technical_id": "hn_item_123457",
        "id": 8864,
        "status": "created"
      }
    ],
    "summary": {
      "total_requested": 2,
      "successfully_created": 2,
      "failed": 0
    }
  },
  "message": "Bulk creation completed successfully"
}
```

## Workflow Transitions

The following transitions are available for HN items:

1. **validate_item**: Triggers validation of the item
2. **store_item**: Triggers storage of validated item
3. **retry_processing**: Retries processing for failed items

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      "Field 'type' is required",
      "Field 'id' must be a positive integer"
    ]
  }
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "HN item not found",
    "details": "No item found with technical_id: hn_item_123456"
  }
}
```

### 409 Conflict
```json
{
  "success": false,
  "error": {
    "code": "ITEM_ALREADY_EXISTS",
    "message": "HN item with this ID already exists",
    "details": "Item with HN ID 8863 already exists with technical_id: hn_item_123456"
  }
}
```

### 422 Unprocessable Entity
```json
{
  "success": false,
  "error": {
    "code": "WORKFLOW_TRANSITION_ERROR",
    "message": "Cannot trigger transition from current state",
    "details": "Transition 'validate_item' not available from state 'stored'"
  }
}
```
