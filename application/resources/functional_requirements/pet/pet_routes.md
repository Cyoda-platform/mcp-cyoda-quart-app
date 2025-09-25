# Pet Routes

## Description
API endpoints for pet data retrieval and display operations.

## Endpoints

### GET /pets
Retrieve all pets with optional filtering
- **Parameters**: 
  - `species` (optional): Filter by pet species
  - `status` (optional): Filter by availability status
  - `categoryId` (optional): Filter by category ID
- **Response**: Array of transformed pet objects

**Request Example**:
```
GET /pets?species=dog&status=available
```

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "id": "pet-123",
      "name": "Buddy",
      "species": "dog",
      "status": "available",
      "categoryId": 1,
      "categoryName": "Dogs",
      "availabilityStatus": "Available for adoption",
      "photoUrls": ["https://example.com/photo1.jpg"],
      "tags": ["friendly", "trained"]
    }
  ],
  "count": 1
}
```

### GET /pets/{id}
Retrieve specific pet by ID
- **Parameters**: `id` (required): Pet identifier
- **Response**: Single transformed pet object

**Request Example**:
```
GET /pets/pet-123
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": "pet-123",
    "name": "Buddy",
    "species": "dog",
    "status": "available",
    "categoryId": 1,
    "categoryName": "Dogs",
    "availabilityStatus": "Available for adoption",
    "photoUrls": ["https://example.com/photo1.jpg"],
    "tags": ["friendly", "trained"]
  }
}
```

### PUT /pets/{id}
Update pet data and trigger workflow transition
- **Parameters**: 
  - `id` (required): Pet identifier
  - `transition` (optional): Workflow transition name
- **Body**: Updated pet data
- **Response**: Updated pet object

**Request Example**:
```
PUT /pets/pet-123?transition=transform_pet_data
Content-Type: application/json

{
  "name": "Buddy Updated",
  "status": "pending"
}
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "id": "pet-123",
    "name": "Buddy Updated",
    "status": "pending",
    "availabilityStatus": "Adoption pending"
  }
}
```
