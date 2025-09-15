# Routes

## SubscriberRoutes

### POST /api/subscribers
**Description:** Register a new subscriber for weekly cat facts
**Transition:** INITIAL (triggers SubscriberWorkflow)

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "subscriptionDate": "2024-01-15T10:30:00Z",
  "isActive": true,
  "state": "ACTIVE"
}
```

### GET /api/subscribers
**Description:** Get all subscribers with pagination and filtering
**Transition:** null

**Query Parameters:**
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)
- `isActive` (optional): Filter by active status
- `email` (optional): Filter by email

**Response:**
```json
{
  "content": [
    {
      "id": 1,
      "email": "john.doe@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "subscriptionDate": "2024-01-15T10:30:00Z",
      "isActive": true,
      "state": "ACTIVE"
    }
  ],
  "totalElements": 1,
  "totalPages": 1,
  "size": 20,
  "number": 0
}
```

### GET /api/subscribers/{id}
**Description:** Get subscriber by ID
**Transition:** null

**Response:**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "subscriptionDate": "2024-01-15T10:30:00Z",
  "isActive": true,
  "state": "ACTIVE"
}
```

### PUT /api/subscribers/{id}
**Description:** Update subscriber information
**Transition:** null

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Smith",
  "transitionName": null
}
```

**Response:**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "firstName": "John",
  "lastName": "Smith",
  "subscriptionDate": "2024-01-15T10:30:00Z",
  "isActive": true,
  "state": "ACTIVE"
}
```

### POST /api/subscribers/{id}/unsubscribe
**Description:** Unsubscribe a subscriber using unsubscribe token
**Transition:** ACTIVE → UNSUBSCRIBED

**Request Body:**
```json
{
  "unsubscribeToken": "abc123def456",
  "transitionName": "ACTIVE_TO_UNSUBSCRIBED"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "isActive": false,
  "state": "UNSUBSCRIBED",
  "message": "Successfully unsubscribed"
}
```

### POST /api/subscribers/{id}/reactivate
**Description:** Reactivate a bounced subscriber
**Transition:** BOUNCED → ACTIVE

**Request Body:**
```json
{
  "transitionName": "BOUNCED_TO_ACTIVE"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "john.doe@example.com",
  "isActive": true,
  "state": "ACTIVE",
  "message": "Successfully reactivated"
}
```

## CatFactRoutes

### POST /api/catfacts/retrieve
**Description:** Manually trigger cat fact retrieval from external API
**Transition:** INITIAL (triggers CatFactWorkflow)

**Request Body:**
```json
{
  "transitionName": "INITIAL"
}
```

**Response:**
```json
{
  "id": 1,
  "fact": "Cats have 32 muscles in each ear.",
  "length": 32,
  "retrievedDate": "2024-01-15T10:30:00Z",
  "state": "RETRIEVED"
}
```

### GET /api/catfacts
**Description:** Get all cat facts with pagination and filtering
**Transition:** null

**Query Parameters:**
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)
- `state` (optional): Filter by state

**Response:**
```json
{
  "content": [
    {
      "id": 1,
      "fact": "Cats have 32 muscles in each ear.",
      "length": 32,
      "retrievedDate": "2024-01-15T10:30:00Z",
      "scheduledSendDate": "2024-01-22T09:00:00Z",
      "state": "SCHEDULED"
    }
  ],
  "totalElements": 1,
  "totalPages": 1,
  "size": 20,
  "number": 0
}
```

### GET /api/catfacts/{id}
**Description:** Get cat fact by ID
**Transition:** null

**Response:**
```json
{
  "id": 1,
  "fact": "Cats have 32 muscles in each ear.",
  "length": 32,
  "retrievedDate": "2024-01-15T10:30:00Z",
  "scheduledSendDate": "2024-01-22T09:00:00Z",
  "actualSendDate": null,
  "state": "SCHEDULED"
}
```

### POST /api/catfacts/{id}/retry
**Description:** Retry failed cat fact distribution
**Transition:** FAILED → SCHEDULED

**Request Body:**
```json
{
  "transitionName": "FAILED_TO_SCHEDULED"
}
```

**Response:**
```json
{
  "id": 1,
  "fact": "Cats have 32 muscles in each ear.",
  "state": "SCHEDULED",
  "message": "Cat fact scheduled for retry"
}
```

## SubscriberInteractionRoutes

### GET /api/subscriber-interactions
**Description:** Get subscriber interactions for reporting
**Transition:** null

**Query Parameters:**
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)
- `subscriberId` (optional): Filter by subscriber ID
- `catFactId` (optional): Filter by cat fact ID
- `interactionType` (optional): Filter by interaction type
- `startDate` (optional): Filter by start date
- `endDate` (optional): Filter by end date

**Response:**
```json
{
  "content": [
    {
      "id": 1,
      "subscriberId": 1,
      "catFactId": 1,
      "interactionType": "EMAIL_SENT",
      "interactionDate": "2024-01-22T09:05:00Z",
      "state": "PROCESSED"
    }
  ],
  "totalElements": 1,
  "totalPages": 1,
  "size": 20,
  "number": 0
}
```

### GET /api/subscriber-interactions/stats
**Description:** Get interaction statistics for reporting
**Transition:** null

**Query Parameters:**
- `startDate` (optional): Start date for statistics
- `endDate` (optional): End date for statistics

**Response:**
```json
{
  "totalSubscribers": 150,
  "activeSubscribers": 142,
  "emailsSent": 142,
  "emailsOpened": 89,
  "emailsClicked": 23,
  "unsubscriptions": 3,
  "openRate": 62.7,
  "clickRate": 16.2,
  "unsubscribeRate": 2.1
}
```

## EmailCampaignRoutes

### POST /api/email-campaigns
**Description:** Create and schedule a new email campaign
**Transition:** INITIAL (triggers EmailCampaignWorkflow)

**Request Body:**
```json
{
  "catFactId": 1,
  "campaignName": "Weekly Cat Facts - Week 3",
  "scheduledDate": "2024-01-22T09:00:00Z",
  "transitionName": "INITIAL"
}
```

**Response:**
```json
{
  "id": 1,
  "catFactId": 1,
  "campaignName": "Weekly Cat Facts - Week 3",
  "scheduledDate": "2024-01-22T09:00:00Z",
  "totalSubscribers": 142,
  "state": "SCHEDULED"
}
```

### GET /api/email-campaigns
**Description:** Get all email campaigns with pagination
**Transition:** null

**Query Parameters:**
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)
- `state` (optional): Filter by state

**Response:**
```json
{
  "content": [
    {
      "id": 1,
      "catFactId": 1,
      "campaignName": "Weekly Cat Facts - Week 3",
      "scheduledDate": "2024-01-22T09:00:00Z",
      "completedDate": "2024-01-22T09:15:00Z",
      "totalSubscribers": 142,
      "emailsSent": 140,
      "emailsFailed": 2,
      "state": "COMPLETED"
    }
  ],
  "totalElements": 1,
  "totalPages": 1,
  "size": 20,
  "number": 0
}
```

### GET /api/email-campaigns/{id}
**Description:** Get email campaign by ID
**Transition:** null

**Response:**
```json
{
  "id": 1,
  "catFactId": 1,
  "campaignName": "Weekly Cat Facts - Week 3",
  "scheduledDate": "2024-01-22T09:00:00Z",
  "startedDate": "2024-01-22T09:00:05Z",
  "completedDate": "2024-01-22T09:15:00Z",
  "totalSubscribers": 142,
  "emailsSent": 140,
  "emailsFailed": 2,
  "state": "COMPLETED"
}
```

### POST /api/email-campaigns/{id}/retry
**Description:** Retry failed email campaign
**Transition:** FAILED → SCHEDULED

**Request Body:**
```json
{
  "transitionName": "FAILED_TO_SCHEDULED"
}
```

**Response:**
```json
{
  "id": 1,
  "campaignName": "Weekly Cat Facts - Week 3",
  "state": "SCHEDULED",
  "message": "Email campaign scheduled for retry"
}
```
