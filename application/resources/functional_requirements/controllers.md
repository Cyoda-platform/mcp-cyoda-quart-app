# Controllers

## MailRoutes

### Description
REST API routes for managing Mail entities and their workflow transitions.

### Base Path
`/api/mails`

---

### Endpoints

#### 1. Create Mail
- **Method**: POST
- **Path**: `/api/mails`
- **Description**: Creates a new mail entity
- **Transition**: null (entity starts in INITIAL state, automatically moves to PENDING)

**Request Example:**
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

**Response Example:**
```json
{
  "id": "mail-123",
  "isHappy": true,
  "mailList": [
    "user1@example.com",
    "user2@example.com", 
    "user3@example.com"
  ],
  "state": "PENDING",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

---

#### 2. Get Mail by ID
- **Method**: GET
- **Path**: `/api/mails/{id}`
- **Description**: Retrieves a specific mail entity by ID

**Response Example:**
```json
{
  "id": "mail-123",
  "isHappy": true,
  "mailList": ["user1@example.com", "user2@example.com"],
  "state": "HAPPY_SENT",
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:31:00Z"
}
```

---

#### 3. Get All Mails
- **Method**: GET
- **Path**: `/api/mails`
- **Description**: Retrieves all mail entities with optional filtering

**Query Parameters:**
- `state` (optional): Filter by entity state
- `isHappy` (optional): Filter by happy/gloomy type

**Response Example:**
```json
{
  "mails": [
    {
      "id": "mail-123",
      "isHappy": true,
      "state": "HAPPY_SENT"
    }
  ],
  "total": 1
}
```

---

#### 4. Update Mail
- **Method**: PUT
- **Path**: `/api/mails/{id}`
- **Description**: Updates mail entity and optionally triggers state transition
- **Transition**: null (no state change, just data update)

**Request Example:**
```json
{
  "isHappy": false,
  "mailList": [
    "newuser@example.com",
    "user2@example.com"
  ],
  "transitionName": null
}
```

**Response Example:**
```json
{
  "id": "mail-123",
  "isHappy": false,
  "mailList": ["newuser@example.com", "user2@example.com"],
  "state": "PENDING"
}
```

---

#### 5. Resend Mail (Happy)
- **Method**: PUT
- **Path**: `/api/mails/{id}/resend`
- **Description**: Triggers resending of mail from HAPPY_SENT back to PENDING
- **Transition**: "HAPPY_SENT_TO_PENDING"

**Request Example:**
```json
{
  "transitionName": "HAPPY_SENT_TO_PENDING"
}
```

**Response Example:**
```json
{
  "id": "mail-123",
  "state": "PENDING",
  "message": "Mail queued for resending"
}
```

---

#### 6. Resend Mail (Gloomy)
- **Method**: PUT
- **Path**: `/api/mails/{id}/resend`
- **Description**: Triggers resending of mail from GLOOMY_SENT back to PENDING
- **Transition**: "GLOOMY_SENT_TO_PENDING"

**Request Example:**
```json
{
  "transitionName": "GLOOMY_SENT_TO_PENDING"
}
```

**Response Example:**
```json
{
  "id": "mail-123",
  "state": "PENDING",
  "message": "Mail queued for resending"
}
```

---

#### 7. Delete Mail
- **Method**: DELETE
- **Path**: `/api/mails/{id}`
- **Description**: Deletes a mail entity

**Response Example:**
```json
{
  "message": "Mail deleted successfully"
}
```
