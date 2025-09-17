# DataAnalysis Routes

## Endpoints

### POST /dataanalysis
Create a new data analysis and start analysis workflow.

**Request:**
```json
{
  "data_source_id": "ds_123456",
  "analysis_type": "statistical",
  "transition": "start_analysis"
}
```

**Response:**
```json
{
  "id": "da_789012",
  "data_source_id": "ds_123456",
  "analysis_type": "statistical",
  "created_at": "2025-09-17T10:10:00Z",
  "status": "pending"
}
```

### GET /dataanalysis/{id}
Retrieve analysis results and status.

**Response:**
```json
{
  "id": "da_789012",
  "data_source_id": "ds_123456",
  "analysis_type": "statistical",
  "results": {
    "total_records": 500,
    "avg_price": 1850000,
    "top_neighborhood": "Chelsea"
  },
  "metrics": {
    "price_range": [420000, 4980000],
    "property_types": {"Apartment": 150, "Detached House": 200}
  },
  "created_at": "2025-09-17T10:15:00Z"
}
```

### PUT /dataanalysis/{id}
Update analysis parameters and optionally trigger transition.

**Request:**
```json
{
  "analysis_type": "summary",
  "transition": "start_analysis"
}
```
