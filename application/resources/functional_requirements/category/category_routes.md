# Category Routes

## Description
REST API endpoints for managing categories in the Purrfect Pets store.

## Endpoints

### GET /categories
Get all categories with optional filtering by status.

**Request Example:**
```
GET /categories?status=active
```

**Response Example:**
```json
[
  {
    "id": "cat-001",
    "name": "Dogs",
    "description": "All dog breeds and puppies",
    "meta": {"state": "active"}
  }
]
```

### GET /categories/{id}
Get a specific category by ID.

**Request Example:**
```
GET /categories/cat-001
```

**Response Example:**
```json
{
  "id": "cat-001",
  "name": "Dogs",
  "description": "All dog breeds and puppies",
  "meta": {"state": "active"}
}
```

### POST /categories
Create a new category.

**Request Example:**
```json
{
  "name": "Cats",
  "description": "All cat breeds and kittens"
}
```

**Response Example:**
```json
{
  "id": "cat-002"
}
```

### PUT /categories/{id}
Update a category with optional transition.

**Request Example:**
```json
{
  "name": "Cats Updated",
  "description": "All feline breeds and kittens",
  "transition": "publish_category"
}
```

**Response Example:**
```json
{
  "success": true
}
```

### DELETE /categories/{id}
Delete a category.

**Request Example:**
```
DELETE /categories/cat-001
```

**Response Example:**
```json
{
  "success": true
}
```
