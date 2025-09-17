# Report Routes

## Endpoints

### POST /report
Create a new report and start generation workflow.

**Request:**
```json
{
  "analysis_id": "da_789012",
  "subscribers": ["user1@example.com", "user2@example.com"],
  "transition": "start_report_generation"
}
```

**Response:**
```json
{
  "id": "rp_345678",
  "analysis_id": "da_789012",
  "subscribers": ["user1@example.com", "user2@example.com"],
  "delivery_status": "pending",
  "created_at": "2025-09-17T10:20:00Z"
}
```

### GET /report/{id}
Retrieve report status and delivery information.

**Response:**
```json
{
  "id": "rp_345678",
  "analysis_id": "da_789012",
  "subscribers": ["user1@example.com", "user2@example.com"],
  "report_content": "London Houses Data Analysis Report...",
  "sent_at": "2025-09-17T10:25:00Z",
  "delivery_status": "sent"
}
```

### PUT /report/{id}
Update report subscribers and optionally trigger transition.

**Request:**
```json
{
  "subscribers": ["user3@example.com"],
  "transition": "start_report_generation"
}
```
