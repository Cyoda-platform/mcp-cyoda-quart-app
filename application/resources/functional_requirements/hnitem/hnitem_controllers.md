# HNItem Controller Requirements

## Controller Name
HNItemController

## Description
Manages Hacker News items with CRUD operations, bulk uploads, Firebase API integration, and hierarchical search.

## Endpoints

### 1. Create Single HN Item
- **Method**: POST
- **Path**: `/hnitem`
- **Request Body**: HN item JSON (Firebase format)
- **Transition**: `validate_item` (nullable)
- **Request Example**:
```json
{
  "id": 8863,
  "type": "story", 
  "by": "dhouston",
  "time": 1175714200,
  "title": "My YC app: Dropbox",
  "url": "http://www.getdropbox.com/u/2/screencast.html",
  "score": 111
}
```
- **Response Example**:
```json
{
  "id": "generated-uuid",
  "status": "created",
  "hn_item_id": 8863
}
```

### 2. Create Multiple HN Items
- **Method**: POST
- **Path**: `/hnitem/batch`
- **Request Body**: Array of HN items
- **Transition**: `validate_item` (nullable)
- **Request Example**:
```json
{
  "items": [
    {"id": 8863, "type": "story", "by": "dhouston", "title": "Dropbox"},
    {"id": 8864, "type": "comment", "by": "user2", "parent": 8863, "text": "Great idea!"}
  ]
}
```

### 3. Bulk Upload from File
- **Method**: POST  
- **Path**: `/hnitem/upload`
- **Content-Type**: multipart/form-data
- **Request**: JSON file upload
- **Transition**: `validate_item` (nullable)

### 4. Trigger Firebase API Pull
- **Method**: POST
- **Path**: `/hnitem/sync/firebase`
- **Request Body**: Sync configuration
- **Request Example**:
```json
{
  "sync_type": "topstories",
  "limit": 100
}
```

### 5. Search HN Items
- **Method**: GET
- **Path**: `/hnitem/search`
- **Query Parameters**: search criteria with parent hierarchy joins
- **Request Example**: `/hnitem/search?type=story&score_min=50&include_children=true`

### 6. Get HN Item by ID
- **Method**: GET
- **Path**: `/hnitem/{id}`
- **Response**: Single HN item with metadata

### 7. Update HN Item
- **Method**: PUT
- **Path**: `/hnitem/{id}`
- **Request Body**: Updated HN item data
- **Transition**: Workflow transition name (nullable)

### 8. Delete HN Item  
- **Method**: DELETE
- **Path**: `/hnitem/{id}`
- **Response**: Deletion confirmation
