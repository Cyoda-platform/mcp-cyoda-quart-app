# Tag API Routes

## Base Route: `/api/tags`

### Endpoints:

**POST /api/tags** - Create new tag
- **Request**: `{"name": "friendly"}`
- **Response**: `{"id": "201", "name": "friendly"}`

**GET /api/tags/{id}** - Get tag by ID
- **Response**: `{"id": "201", "name": "friendly"}`

**PUT /api/tags/{id}** - Update tag
- **Request**: `{"name": "very-friendly"}`
- **Response**: `{"id": "201", "name": "very-friendly"}`

**DELETE /api/tags/{id}** - Delete tag
- **Response**: `{"message": "Tag deleted successfully"}`

**GET /api/tags** - Get all tags
- **Response**: `[{"id": "201", "name": "friendly"}, {"id": "202", "name": "playful"}]`
