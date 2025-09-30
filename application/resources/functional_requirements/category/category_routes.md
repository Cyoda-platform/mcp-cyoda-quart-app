# Category API Routes

## Base Path: `/api/categories`

### GET /api/categories
Get all categories
**Response**: Array of category objects

### GET /api/categories/{id}
Get category by ID
**Response**: Category object

### POST /api/categories
Create new category
**Request**:
```json
{
  "name": "Dogs",
  "description": "All dog breeds available for adoption",
  "imageUrl": "https://example.com/dogs.jpg",
  "isActive": true
}
```
**Response**: Category ID

### PUT /api/categories/{id}
Update category with optional transition
**Request**:
```json
{
  "description": "Updated description",
  "transition": "deactivate_category"
}
```
**Response**: Updated category object

### DELETE /api/categories/{id}
Delete category
**Response**: Success confirmation
