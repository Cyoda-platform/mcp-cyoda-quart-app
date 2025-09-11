# Controllers

## MailRoutes

### Description
REST API endpoints for managing mail entities in the happy mail application. Provides CRUD operations and workflow state transitions for mail processing.

---

### POST /api/mail
**Description**: Create a new mail entity

**Request Body**:
```json
{
    "mailList": "user1@example.com,user2@example.com,user3@example.com",
    "content": "Hello everyone! I hope you're having a wonderful day. I wanted to share some exciting news with you all!",
    "subject": "Exciting News to Share!"
}
```

**Response**:
```json
{
    "id": "12345",
    "mailList": "user1@example.com,user2@example.com,user3@example.com",
    "content": "Hello everyone! I hope you're having a wonderful day. I wanted to share some exciting news with you all!",
    "subject": "Exciting News to Share!",
    "createdAt": "2024-01-15T10:30:00Z",
    "sentAt": null,
    "state": "INITIAL"
}
```

---

### GET /api/mail/{id}
**Description**: Retrieve a specific mail entity by ID

**Response**:
```json
{
    "id": "12345",
    "mailList": "user1@example.com,user2@example.com",
    "content": "I'm feeling quite down today and wanted to reach out for support.",
    "subject": "Need Some Support",
    "createdAt": "2024-01-15T10:30:00Z",
    "sentAt": "2024-01-15T10:35:00Z",
    "state": "SENT"
}
```

---

### GET /api/mail
**Description**: Retrieve all mail entities with optional filtering

**Query Parameters**:
- `state` (optional): Filter by mail state (INITIAL, PENDING_ANALYSIS, HAPPY, GLOOMY, SENT, FAILED)
- `page` (optional): Page number for pagination (default: 0)
- `size` (optional): Page size (default: 20)

**Response**:
```json
{
    "content": [
        {
            "id": "12345",
            "mailList": "user1@example.com",
            "subject": "Happy News!",
            "state": "SENT",
            "createdAt": "2024-01-15T10:30:00Z",
            "sentAt": "2024-01-15T10:35:00Z"
        }
    ],
    "totalElements": 1,
    "totalPages": 1,
    "currentPage": 0
}
```

---

### PUT /api/mail/{id}
**Description**: Update a mail entity and optionally trigger a state transition

**Query Parameters**:
- `transitionName` (optional): Name of the workflow transition to trigger

**Request Body**:
```json
{
    "mailList": "updated@example.com,another@example.com",
    "content": "Updated content with more positive vibes! This is going to be amazing!",
    "subject": "Updated Subject - Great News!",
    "transitionName": null
}
```

**Response**:
```json
{
    "id": "12345",
    "mailList": "updated@example.com,another@example.com",
    "content": "Updated content with more positive vibes! This is going to be amazing!",
    "subject": "Updated Subject - Great News!",
    "createdAt": "2024-01-15T10:30:00Z",
    "sentAt": null,
    "state": "PENDING_ANALYSIS"
}
```

---

### POST /api/mail/{id}/retry
**Description**: Retry processing for failed mail (triggers FAILED → PENDING_ANALYSIS transition)

**Request Body**: Empty

**Response**:
```json
{
    "id": "12345",
    "mailList": "user@example.com",
    "content": "Retry this mail processing",
    "subject": "Retry Mail",
    "createdAt": "2024-01-15T10:30:00Z",
    "sentAt": null,
    "state": "PENDING_ANALYSIS"
}
```

---

### DELETE /api/mail/{id}
**Description**: Delete a mail entity (only allowed for INITIAL, FAILED states)

**Response**: 204 No Content

---

### GET /api/mail/{id}/status
**Description**: Get the current workflow status and available transitions for a mail

**Response**:
```json
{
    "id": "12345",
    "currentState": "HAPPY",
    "availableTransitions": [
        {
            "name": "HAPPY_TO_SENT",
            "targetState": "SENT",
            "processorName": "MailSendHappyMailProcessor"
        },
        {
            "name": "HAPPY_TO_FAILED",
            "targetState": "FAILED",
            "processorName": null
        }
    ]
}
```
