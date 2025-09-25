# Search Routes

## Description
API endpoints for managing search operations and retrieving search results.

## Endpoints

### POST /search
Create new search with parameters and trigger pet data retrieval
- **Body**: Search parameters (species, status, categoryId)
- **Response**: Search entity with initial status

**Request Example**:
```
POST /search
Content-Type: application/json

{
  "species": "dog",
  "status": "available",
  "categoryId": 1
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": "search-456",
    "species": "dog",
    "status": "available",
    "categoryId": 1,
    "searchTimestamp": "2024-01-15T10:30:00Z",
    "resultCount": 0,
    "hasResults": false
  }
}
```

### GET /search/{id}
Retrieve search status and results
- **Parameters**: `id` (required): Search identifier
- **Response**: Search entity with current status and results

**Request Example**:
```
GET /search/search-456
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": "search-456",
    "species": "dog",
    "status": "available",
    "categoryId": 1,
    "searchTimestamp": "2024-01-15T10:30:00Z",
    "resultCount": 5,
    "hasResults": true,
    "notification_message": "Found 5 pets matching your criteria"
  }
}
```

### PUT /search/{id}
Update search parameters and trigger workflow transition
- **Parameters**: 
  - `id` (required): Search identifier
  - `transition` (optional): Workflow transition name
- **Body**: Updated search parameters
- **Response**: Updated search entity

**Request Example**:
```
PUT /search/search-456?transition=notify_results
Content-Type: application/json

{
  "species": "cat",
  "status": "available"
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": "search-456",
    "species": "cat",
    "status": "available",
    "resultCount": 0,
    "hasResults": false,
    "notification_message": "No pets match your search criteria"
  }
}
```
