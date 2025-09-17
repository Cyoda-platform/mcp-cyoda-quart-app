# HNItem Routes

## Base Route: `/hnitem`

### POST /hnitem
Create single HN item
- **Body**: HN item JSON (Firebase format)
- **Transition**: receive_item (optional)

**Request Example**:
```json
{
  "id": 8863,
  "type": "story", 
  "by": "dhouston",
  "time": 1175714200,
  "title": "My YC app: Dropbox",
  "url": "http://www.getdropbox.com/u/2/screencast.html",
  "score": 111,
  "descendants": 71
}
```

**Response Example**:
```json
{
  "id": "generated-uuid",
  "status": "created",
  "transition": "receive_item"
}
```

### POST /hnitem/array
Create multiple HN items
- **Body**: Array of HN item JSONs
- **Transition**: receive_item (optional)

**Request Example**:
```json
[
  {"id": 8863, "type": "story", "by": "dhouston", "title": "Dropbox"},
  {"id": 8864, "type": "comment", "by": "user2", "parent": 8863}
]
```

### POST /hnitem/bulk
Bulk upload from JSON file
- **Body**: File upload or JSON array
- **Transition**: receive_item (optional)

### GET /hnitem/{id}
Retrieve HN item by ID

### GET /hnitem/search
Search HN items with parent hierarchy joins
- **Query params**: q, type, by, parent, limit

**Request Example**:
```
GET /hnitem/search?q=dropbox&type=story&limit=10
```

### PUT /hnitem/{id}
Update HN item
- **Body**: Updated HN item data
- **Transition**: validation_complete, store_item, etc.

### DELETE /hnitem/{id}
Delete HN item

### POST /hnitem/pull-firebase
Trigger pull from Firebase HN API
- **Body**: Optional filters/limits
