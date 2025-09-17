# HNItemCollection Routes

## Base Route: `/hnitemcollection`

### POST /hnitemcollection/array
Create collection from array of HN items
- **Body**: Array of HN items
- **Transition**: receive_collection (optional)

**Request Example**:
```json
{
  "collection_type": "array",
  "items": [
    {"id": 8863, "type": "story", "by": "dhouston", "title": "Dropbox"},
    {"id": 8864, "type": "comment", "by": "user2", "parent": 8863}
  ]
}
```

**Response Example**:
```json
{
  "collection_id": "generated-uuid",
  "status": "received",
  "total_items": 2,
  "transition": "receive_collection"
}
```

### POST /hnitemcollection/file
Create collection from file upload
- **Body**: Multipart file upload (JSON)
- **Transition**: receive_collection (optional)

### POST /hnitemcollection/firebase-pull
Trigger Firebase HN API pull
- **Body**: Pull configuration (limits, filters)
- **Transition**: receive_collection (optional)

**Request Example**:
```json
{
  "collection_type": "firebase_pull",
  "source": "topstories",
  "limit": 100
}
```

### GET /hnitemcollection/{id}
Get collection status and results

**Response Example**:
```json
{
  "collection_id": "uuid",
  "collection_type": "array",
  "total_items": 100,
  "processed_items": 95,
  "failed_items": 5,
  "status": "processing"
}
```

### PUT /hnitemcollection/{id}
Update collection or trigger processing
- **Transition**: start_processing, etc.

### GET /hnitemcollection/{id}/errors
Get processing errors for collection
