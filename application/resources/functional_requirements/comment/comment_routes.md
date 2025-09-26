# Comment Routes

## Base Path: `/api/comments`

### POST /api/comments
Create a new comment for ingestion.

**Request Example:**
```json
{
  "source_api": "reddit",
  "external_id": "abc123",
  "content": "This is a sample comment",
  "author": "user123",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {"likes": 5, "replies": 2}
}
```

**Response Example:**
```json
{
  "id": "comment-uuid-123",
  "status": "created"
}
```

### GET /api/comments/{id}
Retrieve a specific comment by ID.

**Response Example:**
```json
{
  "id": "comment-uuid-123",
  "source_api": "reddit",
  "external_id": "abc123",
  "content": "This is a sample comment",
  "author": "user123",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {"likes": 5, "replies": 2},
  "ingested_at": "2024-01-15T10:35:00Z",
  "meta": {"state": "validated"}
}
```

### PUT /api/comments/{id}
Update a comment and optionally trigger workflow transition.

**Request Example:**
```json
{
  "content": "Updated comment content",
  "transition": "validate_comment"
}
```

**Response Example:**
```json
{
  "id": "comment-uuid-123",
  "status": "updated",
  "new_state": "validated"
}
```

### GET /api/comments
List all comments with optional filtering.

**Query Parameters:**
- `source_api`: Filter by API source
- `state`: Filter by workflow state
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response Example:**
```json
{
  "comments": [
    {
      "id": "comment-uuid-123",
      "source_api": "reddit",
      "content": "Sample comment",
      "meta": {"state": "validated"}
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```
