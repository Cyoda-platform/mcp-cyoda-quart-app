# Pet Routes

## Description
REST API endpoints for managing pets in the Purrfect Pets store.

## Endpoints

### GET /pets
Get all pets with optional filtering by status.

**Request Example:**
```
GET /pets?status=available
```

**Response Example:**
```json
[
  {
    "id": "pet-123",
    "name": "Fluffy",
    "category": "cat-001",
    "photo_urls": ["https://example.com/fluffy1.jpg"],
    "tags": ["friendly", "indoor"],
    "meta": {"state": "available"}
  }
]
```

### GET /pets/{id}
Get a specific pet by ID.

**Request Example:**
```
GET /pets/pet-123
```

**Response Example:**
```json
{
  "id": "pet-123",
  "name": "Fluffy",
  "category": "cat-001",
  "photo_urls": ["https://example.com/fluffy1.jpg"],
  "tags": ["friendly", "indoor"],
  "meta": {"state": "available"}
}
```

### POST /pets
Create a new pet.

**Request Example:**
```json
{
  "name": "Buddy",
  "category": "dog-001",
  "photo_urls": ["https://example.com/buddy1.jpg"],
  "tags": ["playful", "outdoor"]
}
```

**Response Example:**
```json
{
  "id": "pet-124"
}
```

### PUT /pets/{id}
Update a pet with optional transition.

**Request Example:**
```json
{
  "name": "Buddy Updated",
  "category": "dog-001",
  "photo_urls": ["https://example.com/buddy2.jpg"],
  "tags": ["playful", "trained"],
  "transition": "reserve_pet"
}
```

**Response Example:**
```json
{
  "success": true
}
```

### DELETE /pets/{id}
Delete a pet.

**Request Example:**
```
DELETE /pets/pet-123
```

**Response Example:**
```json
{
  "success": true
}
```
