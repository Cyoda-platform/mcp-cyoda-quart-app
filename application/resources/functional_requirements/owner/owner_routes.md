# Owner Routes

## Base Route: `/owners`

### GET /owners
Get all owners with optional filtering.

**Request Example:**
```
GET /owners?status=verified&experience=experienced
```

**Response Example:**
```json
[
  {
    "id": "owner123",
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "555-0123",
    "experience": "experienced",
    "status": "verified"
  }
]
```

### POST /owners
Register a new owner.

**Request Example:**
```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "555-0456",
  "address": "123 Main St, City, State",
  "experience": "beginner",
  "preferences": "Small dogs, cats"
}
```

**Response Example:**
```json
{
  "id": "owner124",
  "message": "Owner registered successfully"
}
```

### GET /owners/{id}
Get specific owner by ID.

**Response Example:**
```json
{
  "id": "owner123",
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "555-0123",
  "address": "456 Oak Ave, City, State",
  "experience": "experienced",
  "preferences": "Large dogs",
  "status": "verified"
}
```

### PUT /owners/{id}
Update owner with optional transition.

**Request Example:**
```json
{
  "verification_documents": "documents_uploaded.pdf",
  "transition": "verify_owner"
}
```

**Response Example:**
```json
{
  "id": "owner123",
  "message": "Owner updated successfully",
  "new_status": "verified"
}
```
