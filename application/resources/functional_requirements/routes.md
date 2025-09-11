# Routes

## MailRoutes

### Description
API routes for managing Mail entities and their workflow transitions.

---

### POST /api/mail
**Description**: Create a new mail entity

**Request Body**:
```json
{
    "isHappy": true,
    "mailList": [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ]
}
```

**Response**:
```json
{
    "id": "mail-123",
    "isHappy": true,
    "mailList": [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ],
    "state": "pending",
    "createdAt": "2024-01-15T10:30:00Z"
}
```

**Status Codes**:
- 201: Mail created successfully
- 400: Invalid request data

---

### GET /api/mail/{id}
**Description**: Retrieve a specific mail entity by ID

**Response**:
```json
{
    "id": "mail-123",
    "isHappy": true,
    "mailList": [
        "user1@example.com",
        "user2@example.com"
    ],
    "state": "happy_sent",
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:31:00Z"
}
```

**Status Codes**:
- 200: Mail retrieved successfully
- 404: Mail not found

---

### GET /api/mail
**Description**: Retrieve all mail entities with optional filtering

**Query Parameters**:
- `state` (optional): Filter by mail state
- `isHappy` (optional): Filter by happiness state

**Example Request**: `GET /api/mail?state=pending&isHappy=true`

**Response**:
```json
{
    "mails": [
        {
            "id": "mail-123",
            "isHappy": true,
            "mailList": ["user1@example.com"],
            "state": "pending",
            "createdAt": "2024-01-15T10:30:00Z"
        }
    ],
    "total": 1
}
```

---

### PUT /api/mail/{id}
**Description**: Update a mail entity with optional state transition

**Query Parameters**:
- `transition` (optional): Transition name to execute after update

**Request Body**:
```json
{
    "isHappy": false,
    "mailList": [
        "user1@example.com",
        "user4@example.com"
    ],
    "transition": null
}
```

**Response**:
```json
{
    "id": "mail-123",
    "isHappy": false,
    "mailList": [
        "user1@example.com",
        "user4@example.com"
    ],
    "state": "pending",
    "updatedAt": "2024-01-15T10:35:00Z"
}
```

**Status Codes**:
- 200: Mail updated successfully
- 404: Mail not found
- 400: Invalid request data

---

### POST /api/mail/{id}/transition
**Description**: Execute a specific workflow transition

**Request Body**:
```json
{
    "transition": "failed_to_pending"
}
```

**Response**:
```json
{
    "id": "mail-123",
    "isHappy": true,
    "mailList": ["user1@example.com"],
    "state": "pending",
    "updatedAt": "2024-01-15T10:40:00Z"
}
```

**Available Transitions**:
- `failed_to_pending`: Manual retry for failed mails

**Status Codes**:
- 200: Transition executed successfully
- 404: Mail not found
- 400: Invalid transition or current state doesn't allow transition

---

### DELETE /api/mail/{id}
**Description**: Delete a mail entity

**Status Codes**:
- 204: Mail deleted successfully
- 404: Mail not found

### Notes
- All endpoints return appropriate HTTP status codes
- Request validation ensures data integrity
- State transitions are validated against the current entity state
- The API automatically triggers workflow transitions when mails are created
