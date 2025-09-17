# Adoption Routes

## Base Route: `/adoptions`

### GET /adoptions
Get all adoptions with optional filtering.

**Request Example:**
```
GET /adoptions?status=pending&owner_id=owner123
```

**Response Example:**
```json
[
  {
    "id": "adoption123",
    "pet_id": "pet456",
    "owner_id": "owner789",
    "application_date": "2024-01-15T10:00:00Z",
    "status": "pending",
    "fee_paid": 150
  }
]
```

### POST /adoptions
Submit a new adoption application.

**Request Example:**
```json
{
  "pet_id": "pet456",
  "owner_id": "owner789",
  "notes": "Very excited to adopt this pet",
  "fee_paid": 150
}
```

**Response Example:**
```json
{
  "id": "adoption124",
  "message": "Adoption application submitted successfully"
}
```

### GET /adoptions/{id}
Get specific adoption by ID.

**Response Example:**
```json
{
  "id": "adoption123",
  "pet_id": "pet456",
  "owner_id": "owner789",
  "application_date": "2024-01-15T10:00:00Z",
  "adoption_date": null,
  "notes": "Very excited to adopt this pet",
  "fee_paid": 150,
  "contract_signed": false,
  "status": "pending"
}
```

### PUT /adoptions/{id}
Update adoption with optional transition.

**Request Example:**
```json
{
  "contract_signed": true,
  "transition": "approve_application"
}
```

**Response Example:**
```json
{
  "id": "adoption123",
  "message": "Adoption updated successfully",
  "new_status": "approved"
}
```
