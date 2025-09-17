# DataSource Routes

## Endpoints

### POST /datasource
Create a new data source and start download workflow.

**Request:**
```json
{
  "url": "https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/ai-2.x/data/test-inputs/v1/connections/london_houses.csv",
  "data_format": "csv",
  "transition": "start_download"
}
```

**Response:**
```json
{
  "id": "ds_123456",
  "url": "https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/ai-2.x/data/test-inputs/v1/connections/london_houses.csv",
  "data_format": "csv",
  "status": "pending",
  "created_at": "2025-09-17T10:00:00Z"
}
```

### GET /datasource/{id}
Retrieve data source status and information.

**Response:**
```json
{
  "id": "ds_123456",
  "url": "https://raw.githubusercontent.com/Cyoda-platform/cyoda-ai/refs/heads/ai-2.x/data/test-inputs/v1/connections/london_houses.csv",
  "data_format": "csv",
  "last_downloaded": "2025-09-17T10:05:00Z",
  "file_size": 45678,
  "status": "completed"
}
```

### PUT /datasource/{id}
Update data source and optionally trigger transition.

**Request:**
```json
{
  "url": "https://new-url.com/data.csv",
  "transition": "start_download"
}
```
