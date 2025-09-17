# HN Item Routes

## Overview
REST API endpoints for managing Hacker News items with support for single items, arrays, bulk uploads, Firebase API integration, and hierarchical search.

## Endpoints

### 1. POST /hnitem
Create a single HN item
- **Transition**: `validate_item` (nullable)
- **Request**: Single HN item JSON
- **Response**: Created item ID

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
  "descendants": 71
}
```

**Response Example**:
```json
{
  "id": "generated-uuid",
  "status": "created"
}
```

### 2. POST /hnitem/batch
Create multiple HN items
- **Transition**: `validate_item` (nullable)
- **Request**: Array of HN item JSON objects
- **Response**: Array of created item IDs

### 3. POST /hnitem/bulk-upload
Bulk upload from JSON file
- **Transition**: `validate_item` (nullable)
- **Request**: Multipart form with JSON file
- **Response**: Upload status and item count

### 4. POST /hnitem/firebase-sync
Trigger Firebase HN API data pull
- **Transition**: `process_item` (nullable)
- **Request**: Sync parameters (item IDs, story types)
- **Response**: Sync job status

### 5. GET /hnitem/search
Search HN items with parent hierarchy joins
- **Query Parameters**: text, type, author, parent_id, include_children
- **Response**: Matching items with parent/child relationships

**Request Example**:
```
GET /hnitem/search?type=story&author=dhouston&include_children=true
```

**Response Example**:
```json
{
  "items": [
    {
      "id": "uuid",
      "hn_id": 8863,
      "type": "story",
      "title": "My YC app: Dropbox",
      "children": [...]
    }
  ],
  "total": 1
}
```
