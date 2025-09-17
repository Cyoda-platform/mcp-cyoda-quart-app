# Pet Routes

## Base Route: `/pets`

### GET /pets
Get all pets with optional filtering.

**Request Example:**
```
GET /pets?species=cat&status=available
```

**Response Example:**
```json
[
  {
    "id": "pet123",
    "name": "Fluffy",
    "species": "cat",
    "breed": "Persian",
    "age": 3,
    "description": "Friendly and playful",
    "adoption_fee": 150
  }
]
```

### POST /pets
Create a new pet.

**Request Example:**
```json
{
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "age": 2,
  "description": "Energetic and loyal",
  "medical_history": "Vaccinated, neutered",
  "adoption_fee": 200
}
```

**Response Example:**
```json
{
  "id": "pet124",
  "message": "Pet created successfully"
}
```

### GET /pets/{id}
Get specific pet by ID.

**Response Example:**
```json
{
  "id": "pet123",
  "name": "Fluffy",
  "species": "cat",
  "breed": "Persian",
  "age": 3,
  "description": "Friendly and playful",
  "medical_history": "Vaccinated, spayed",
  "adoption_fee": 150,
  "status": "available"
}
```

### PUT /pets/{id}
Update pet with optional transition.

**Request Example:**
```json
{
  "name": "Fluffy Updated",
  "description": "Very friendly cat",
  "transition": "reserve_pet"
}
```

**Response Example:**
```json
{
  "id": "pet123",
  "message": "Pet updated successfully",
  "new_status": "reserved"
}
```
