# Category API Routes

## Base Route: `/api/categories`

### Endpoints:

**POST /api/categories** - Create new category
- **Request**: `{"name": "Dogs"}`
- **Response**: `{"id": "101", "name": "Dogs"}`

**GET /api/categories/{id}** - Get category by ID
- **Response**: `{"id": "101", "name": "Dogs"}`

**PUT /api/categories/{id}** - Update category
- **Request**: `{"name": "Canines"}`
- **Response**: `{"id": "101", "name": "Canines"}`

**DELETE /api/categories/{id}** - Delete category
- **Response**: `{"message": "Category deleted successfully"}`

**GET /api/categories** - Get all categories
- **Response**: `[{"id": "101", "name": "Dogs"}, {"id": "102", "name": "Cats"}]`
