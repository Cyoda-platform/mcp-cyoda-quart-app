# Report Routes

## Base Path: `/api/reports`

### POST /api/reports
Create a new report for a specific period.

**Request Example:**
```json
{
  "title": "Weekly Comment Analysis Report",
  "recipient_email": "admin@example.com",
  "report_period_start": "2024-01-08T00:00:00Z",
  "report_period_end": "2024-01-15T23:59:59Z"
}
```

**Response Example:**
```json
{
  "id": "report-uuid-789",
  "status": "created"
}
```

### GET /api/reports/{id}
Retrieve a specific report by ID.

**Response Example:**
```json
{
  "id": "report-uuid-789",
  "title": "Weekly Comment Analysis Report",
  "recipient_email": "admin@example.com",
  "report_period_start": "2024-01-08T00:00:00Z",
  "report_period_end": "2024-01-15T23:59:59Z",
  "summary_data": {
    "total_comments": 150,
    "avg_sentiment": 0.65,
    "top_keywords": ["great", "good", "excellent"],
    "toxicity_summary": {"low": 140, "medium": 8, "high": 2}
  },
  "generated_at": "2024-01-16T09:00:00Z",
  "email_sent_at": "2024-01-16T09:05:00Z",
  "meta": {"state": "sent"}
}
```

### PUT /api/reports/{id}
Update a report and optionally trigger workflow transition.

**Request Example:**
```json
{
  "title": "Updated Report Title",
  "transition": "send_email"
}
```

**Response Example:**
```json
{
  "id": "report-uuid-789",
  "status": "updated",
  "new_state": "sent"
}
```

### GET /api/reports
List all reports with optional filtering.

**Query Parameters:**
- `recipient_email`: Filter by recipient
- `state`: Filter by workflow state
- `period_start`: Filter by start date
- `period_end`: Filter by end date
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response Example:**
```json
{
  "reports": [
    {
      "id": "report-uuid-789",
      "title": "Weekly Comment Analysis Report",
      "recipient_email": "admin@example.com",
      "meta": {"state": "sent"}
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```
