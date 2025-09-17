# HNItem Routes Requirements

## Base Route: `/hnitem`

## Endpoints

### POST /hnitem
Create a single HN item
- **Body**: HN item JSON data
- **Transition**: Optional transition name

**Request Example:**
```json
{
  "data": {
    "id": 8863,
    "type": "story",
    "by": "dhouston",
    "time": 1175714200,
    "title": "My YC app: Dropbox",
    "url": "http://www.getdropbox.com/u/2/screencast.html",
    "score": 111,
    "descendants": 71
  },
  "transition": "validation_complete"
}
```

**Response Example:**
```json
{
  "id": "generated-uuid",
  "status": "success"
}
```

### POST /hnitem/bulk
Create multiple HN items
- **Body**: Array of HN item JSON data

**Request Example:**
```json
{
  "items": [
    {
      "id": 8863,
      "type": "story",
      "by": "dhouston",
      "title": "Dropbox Story"
    },
    {
      "id": 8864,
      "type": "comment",
      "by": "user2",
      "parent": 8863,
      "text": "Great idea!"
    }
  ]
}
```

### GET /hnitem/{id}
Retrieve specific HN item

**Response Example:**
```json
{
  "id": "uuid",
  "data": {
    "id": 8863,
    "type": "story",
    "title": "Dropbox Story"
  },
  "meta": {
    "state": "active"
  }
}
```

### GET /hnitem/search
Search HN items with query parameters
- **Query**: search terms, filters, parent hierarchy joins

**Request Example:**
```
GET /hnitem/search?q=dropbox&type=story&include_children=true
```
