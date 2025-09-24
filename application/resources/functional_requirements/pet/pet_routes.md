# Pet API Routes

## Base Path: `/api/pets`

### 1. Create Pet
- **Method**: POST
- **Path**: `/api/pets`
- **Request Body**:
```json
{
  "name": "Fluffy",
  "category": {"id": 1, "name": "Cats"},
  "photoUrls": ["https://example.com/fluffy1.jpg"],
  "tags": [{"id": 1, "name": "friendly"}],
  "breed": "Persian",
  "age": 12,
  "price": 500.00
}
```
- **Response**:
```json
{
  "id": "pet-123",
  "status": "success",
  "message": "Pet created successfully"
}
```

### 2. Get Pet by ID
- **Method**: GET
- **Path**: `/api/pets/{petId}`
- **Response**:
```json
{
  "id": "pet-123",
  "name": "Fluffy",
  "category": {"id": 1, "name": "Cats"},
  "photoUrls": ["https://example.com/fluffy1.jpg"],
  "tags": [{"id": 1, "name": "friendly"}],
  "breed": "Persian",
  "age": 12,
  "price": 500.00,
  "state": "available"
}
```

### 3. Update Pet
- **Method**: PUT
- **Path**: `/api/pets/{petId}`
- **Query Parameters**: `transition` (optional) - transition name for state change
- **Request Body**:
```json
{
  "name": "Fluffy Updated",
  "price": 450.00,
  "transition": "reserve_pet"
}
```
- **Response**:
```json
{
  "id": "pet-123",
  "status": "success",
  "message": "Pet updated and transitioned to pending"
}
```

### 4. Delete Pet
- **Method**: DELETE
- **Path**: `/api/pets/{petId}`
- **Response**:
```json
{
  "status": "success",
  "message": "Pet deleted successfully"
}
```

### 5. List Pets
- **Method**: GET
- **Path**: `/api/pets`
- **Query Parameters**: `status`, `category`, `limit`, `offset`
- **Response**:
```json
{
  "pets": [...],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```
