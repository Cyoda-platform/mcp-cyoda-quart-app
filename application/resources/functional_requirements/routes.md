# Routes

## MailRoutes

### Description
REST API endpoints for managing Mail entities and their workflow transitions.

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
    "state": "PENDING"
}
```

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
    "state": "HAPPY_SENT"
}
```

---

### GET /api/mail
**Description**: Retrieve all mail entities

**Response**:
```json
[
    {
        "id": "mail-123",
        "isHappy": true,
        "mailList": ["user1@example.com"],
        "state": "HAPPY_SENT"
    },
    {
        "id": "mail-124",
        "isHappy": false,
        "mailList": ["user2@example.com"],
        "state": "GLOOMY_SENT"
    }
]
```

---

### PUT /api/mail/{id}
**Description**: Update a mail entity

**Query Parameters**:
- `transitionName` (optional): Name of the workflow transition to trigger

**Request Body**:
```json
{
    "isHappy": false,
    "mailList": [
        "updated@example.com",
        "another@example.com"
    ]
}
```

**Response**:
```json
{
    "id": "mail-123",
    "isHappy": false,
    "mailList": [
        "updated@example.com",
        "another@example.com"
    ],
    "state": "PENDING"
}
```

---

### POST /api/mail/{id}/retry
**Description**: Retry failed mail delivery (manual transition from FAILED to PENDING)

**Query Parameters**:
- `transitionName`: "FAILED_TO_PENDING"

**Request Body**: None

**Response**:
```json
{
    "id": "mail-123",
    "isHappy": true,
    "mailList": ["user@example.com"],
    "state": "PENDING"
}
```

---

### DELETE /api/mail/{id}
**Description**: Delete a mail entity

**Response**: 204 No Content
