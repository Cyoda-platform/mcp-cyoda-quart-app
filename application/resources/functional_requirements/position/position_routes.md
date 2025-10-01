# Position API Routes

## Base Path: `/api/positions`

### Create Position
- **POST** `/api/positions`
- **Request Body**:
```json
{
  "title": "Senior Software Engineer",
  "description": "Lead development of software solutions",
  "department": "Engineering",
  "level": "Senior",
  "salary_range_min": 80000,
  "salary_range_max": 120000
}
```
- **Response**:
```json
{
  "id": "pos-789",
  "title": "Senior Software Engineer",
  "description": "Lead development of software solutions",
  "department": "Engineering",
  "level": "Senior",
  "salary_range_min": 80000,
  "salary_range_max": 120000,
  "is_active": true,
  "meta": {"state": "active"}
}
```

### Get Position
- **GET** `/api/positions/{id}`
- **Response**: Position object with current state

### Update Position
- **PUT** `/api/positions/{id}`
- **Request Body**: Position fields to update + optional transition
```json
{
  "salary_range_max": 130000,
  "transition": "deactivate_position"
}
```

### List Positions
- **GET** `/api/positions`
- **Query Parameters**: `page`, `limit`, `state`, `department`, `level`
- **Response**: Paginated list of positions

### Delete Position
- **DELETE** `/api/positions/{id}`

### Position Transitions
- **POST** `/api/positions/{id}/transitions`
- **Request Body**:
```json
{
  "transition": "deactivate_position"
}
```
