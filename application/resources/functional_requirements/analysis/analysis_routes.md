# Analysis Routes

## Base Path: `/api/analyses`

### POST /api/analyses
Create a new analysis for a comment.

**Request Example:**
```json
{
  "comment_id": "comment-uuid-123"
}
```

**Response Example:**
```json
{
  "id": "analysis-uuid-456",
  "status": "created"
}
```

### GET /api/analyses/{id}
Retrieve a specific analysis by ID.

**Response Example:**
```json
{
  "id": "analysis-uuid-456",
  "comment_id": "comment-uuid-123",
  "sentiment_score": 0.75,
  "sentiment_label": "positive",
  "keywords": ["great", "amazing", "love"],
  "language": "en",
  "toxicity_score": 0.1,
  "analyzed_at": "2024-01-15T10:40:00Z",
  "meta": {"state": "completed"}
}
```

### PUT /api/analyses/{id}
Update an analysis and optionally trigger workflow transition.

**Request Example:**
```json
{
  "sentiment_score": 0.8,
  "transition": "complete_analysis"
}
```

**Response Example:**
```json
{
  "id": "analysis-uuid-456",
  "status": "updated",
  "new_state": "completed"
}
```

### GET /api/analyses
List all analyses with optional filtering.

**Query Parameters:**
- `comment_id`: Filter by comment ID
- `sentiment_label`: Filter by sentiment (positive, negative, neutral)
- `state`: Filter by workflow state
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response Example:**
```json
{
  "analyses": [
    {
      "id": "analysis-uuid-456",
      "comment_id": "comment-uuid-123",
      "sentiment_label": "positive",
      "meta": {"state": "completed"}
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```
