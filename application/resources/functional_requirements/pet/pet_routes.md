# Pet API Routes

## Base Route: `/api/pets`

### Endpoints:

**POST /api/pets** - Create new pet
- **Request**: `{"name": "Buddy", "category": {"id": 1, "name": "Dogs"}, "photoUrls": ["http://example.com/photo1.jpg"], "tags": [{"id": 1, "name": "friendly"}], "status": "available"}`
- **Response**: `{"id": "123", "name": "Buddy", "category": {"id": 1, "name": "Dogs"}, "photoUrls": ["http://example.com/photo1.jpg"], "tags": [{"id": 1, "name": "friendly"}], "status": "available"}`

**GET /api/pets/{id}** - Get pet by ID
- **Response**: `{"id": "123", "name": "Buddy", "category": {"id": 1, "name": "Dogs"}, "photoUrls": ["http://example.com/photo1.jpg"], "tags": [{"id": 1, "name": "friendly"}], "status": "available"}`

**PUT /api/pets/{id}** - Update pet with optional transition
- **Request**: `{"name": "Buddy Updated", "status": "pending", "transition": "reserve_pet"}`
- **Response**: `{"id": "123", "name": "Buddy Updated", "status": "pending"}`

**DELETE /api/pets/{id}** - Delete pet
- **Response**: `{"message": "Pet deleted successfully"}`

**GET /api/pets/findByStatus?status=available** - Find pets by status
- **Response**: `[{"id": "123", "name": "Buddy", "status": "available"}]`
