# HN Item Controller Requirements

## Controller Name
HnItemController

## Description
REST API controller for managing Hacker News items with support for single items, arrays, bulk uploads, Firebase API integration, and hierarchical search.

## Endpoints

### 1. POST /api/hnitem
**Purpose**: Create a single HN item
**Method**: POST
**Request Body**: Single HnItem object
**Transition**: validate_item (nullable)

**Request Example**:
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
  "kids": [8952, 9224, 8917, 8884, 8887]
}
```

**Response Example**:
```json
{
  "id": "generated-uuid",
  "hn_id": 8863,
  "status": "created",
  "workflow_state": "pending_validation"
}
```

### 2. POST /api/hnitem/batch
**Purpose**: Create multiple HN items from an array
**Method**: POST
**Request Body**: Array of HnItem objects
**Transition**: validate_item (nullable)

**Request Example**:
```json
[
  {
    "id": 8863,
    "type": "story",
    "by": "dhouston",
    "title": "My YC app: Dropbox"
  },
  {
    "id": 2921983,
    "type": "comment",
    "by": "norvig",
    "parent": 2921506,
    "text": "Great comment here"
  }
]
```

**Response Example**:
```json
{
  "created_count": 2,
  "items": [
    {
      "id": "uuid-1",
      "hn_id": 8863,
      "status": "created"
    },
    {
      "id": "uuid-2", 
      "hn_id": 2921983,
      "status": "created"
    }
  ]
}
```

### 3. POST /api/hnitem/bulk-upload
**Purpose**: Bulk upload HN items from JSON file
**Method**: POST
**Content-Type**: multipart/form-data
**Request Body**: JSON file containing array of HnItem objects
**Transition**: validate_item (nullable)

**Request Example**:
```
Content-Type: multipart/form-data
file: hnitem_data.json (containing array of HN items)
```

**Response Example**:
```json
{
  "uploaded_count": 150,
  "processed_count": 148,
  "failed_count": 2,
  "batch_id": "batch-uuid-123"
}
```

### 4. POST /api/hnitem/fetch-firebase
**Purpose**: Trigger fetching data from Firebase HN API
**Method**: POST
**Request Body**: Configuration for Firebase fetch
**Transition**: validate_item (nullable)

**Request Example**:
```json
{
  "fetch_type": "topstories",
  "limit": 100,
  "include_comments": true
}
```

**Response Example**:
```json
{
  "fetch_id": "fetch-uuid-456",
  "status": "initiated",
  "estimated_items": 100,
  "fetch_type": "topstories"
}
```

### 5. GET /api/hnitem/{id}
**Purpose**: Retrieve a single HN item by ID
**Method**: GET
**Path Parameters**: id (string) - Entity ID

**Response Example**:
```json
{
  "id": "uuid-123",
  "hn_id": 8863,
  "type": "story",
  "by": "dhouston",
  "title": "My YC app: Dropbox",
  "workflow_state": "processed",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 6. GET /api/hnitem
**Purpose**: List HN items with pagination and filtering
**Method**: GET
**Query Parameters**: 
- page (integer, default: 1)
- limit (integer, default: 20, max: 100)
- type (string, optional): Filter by item type
- author (string, optional): Filter by author

**Response Example**:
```json
{
  "items": [
    {
      "id": "uuid-123",
      "hn_id": 8863,
      "type": "story",
      "title": "My YC app: Dropbox"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1500,
    "total_pages": 75
  }
}
```

### 7. GET /api/hnitem/search
**Purpose**: Search HN items with hierarchical parent joins
**Method**: GET
**Query Parameters**:
- q (string): Search query
- include_parents (boolean, default: false): Include parent hierarchy
- include_children (boolean, default: false): Include child comments

**Request Example**:
```
GET /api/hnitem/search?q=dropbox&include_parents=true&include_children=true
```

**Response Example**:
```json
{
  "results": [
    {
      "item": {
        "id": "uuid-123",
        "hn_id": 8863,
        "type": "story",
        "title": "My YC app: Dropbox"
      },
      "parents": [],
      "children": [
        {
          "id": "uuid-456",
          "hn_id": 8952,
          "type": "comment",
          "parent": 8863
        }
      ]
    }
  ],
  "total_results": 25
}
```

### 8. PUT /api/hnitem/{id}/transition
**Purpose**: Trigger workflow transition for an HN item
**Method**: PUT
**Path Parameters**: id (string) - Entity ID
**Request Body**: Transition details

**Request Example**:
```json
{
  "transition": "process_item"
}
```

**Response Example**:
```json
{
  "id": "uuid-123",
  "previous_state": "validated",
  "new_state": "processed",
  "transition": "process_item",
  "timestamp": "2024-01-15T10:35:00Z"
}
```
