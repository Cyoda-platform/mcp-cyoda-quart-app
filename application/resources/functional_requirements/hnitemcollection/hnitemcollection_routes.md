# HNItemCollection Routes Requirements

## Base Route: `/hnitemcollection`

## Endpoints

### POST /hnitemcollection
Create a new collection
- **Body**: Collection metadata and optional items
- **Transition**: Optional transition name

**Request Example:**
```json
{
  "data": {
    "name": "Daily HN Stories",
    "source": "firebase_api",
    "metadata": {
      "fetch_type": "topstories",
      "limit": 100
    }
  },
  "transition": "begin_processing"
}
```

**Response Example:**
```json
{
  "id": "collection-uuid",
  "status": "success"
}
```

### POST /hnitemcollection/bulk-upload
Upload items from JSON file
- **Body**: File upload with HN items array

**Request Example:**
```json
{
  "collection_name": "Bulk Upload 2024",
  "items": [
    {
      "id": 8863,
      "type": "story",
      "title": "Story 1"
    },
    {
      "id": 8864,
      "type": "comment",
      "text": "Comment 1"
    }
  ]
}
```

### POST /hnitemcollection/firebase-pull
Trigger Firebase API pull
- **Body**: API parameters

**Request Example:**
```json
{
  "collection_name": "Firebase Pull",
  "api_endpoint": "topstories",
  "limit": 50
}
```

### GET /hnitemcollection/{id}
Get collection status and results

**Response Example:**
```json
{
  "id": "uuid",
  "data": {
    "name": "Daily HN Stories",
    "total_items": 100,
    "processed_items": 95,
    "failed_items": 5
  },
  "meta": {
    "state": "partial_failure"
  }
}
```
