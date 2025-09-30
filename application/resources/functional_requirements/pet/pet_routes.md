# Pet API Routes

## Base Path: `/api/pets`

### GET /api/pets
Get all pets
**Response**: Array of pet objects

### GET /api/pets/{id}
Get pet by ID
**Response**: Pet object

### POST /api/pets
Create new pet
**Request**:
```json
{
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age": 3,
  "color": "golden",
  "size": "large",
  "price": 500,
  "description": "Friendly family dog",
  "categoryId": "cat-001",
  "imageUrl": "https://example.com/buddy.jpg",
  "healthStatus": "healthy"
}
```
**Response**: Pet ID

### PUT /api/pets/{id}
Update pet with optional transition
**Request**:
```json
{
  "name": "Buddy Updated",
  "price": 450,
  "transition": "reserve_pet"
}
```
**Response**: Updated pet object

### DELETE /api/pets/{id}
Delete pet
**Response**: Success confirmation
