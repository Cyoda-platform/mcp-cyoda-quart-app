# Routes

## SubscriberRoutes

### 1. POST /api/subscribers
**Description**: Register a new subscriber for weekly cat facts.
**Transition**: Uses transition to move from INITIAL to PENDING state.

**Request Body**:
```json
{
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe"
}
```

**Response Body**:
```json
{
    "id": 1,
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "subscriptionDate": "2024-01-15T10:30:00Z",
    "isActive": false,
    "state": "PENDING"
}
```

### 2. PUT /api/subscribers/{id}/activate
**Description**: Activate a subscriber (email verification).
**Transition**: activate-subscriber (PENDING → ACTIVE)

**Request Body**:
```json
{
    "transitionName": "activate-subscriber"
}
```

**Response Body**:
```json
{
    "id": 1,
    "email": "user@example.com",
    "isActive": true,
    "state": "ACTIVE"
}
```

### 3. PUT /api/subscribers/{id}/unsubscribe
**Description**: Unsubscribe a subscriber.
**Transition**: unsubscribe (ACTIVE/PENDING → UNSUBSCRIBED)

**Request Body**:
```json
{
    "transitionName": "unsubscribe"
}
```

**Response Body**:
```json
{
    "id": 1,
    "email": "user@example.com",
    "isActive": false,
    "state": "UNSUBSCRIBED"
}
```

### 4. POST /api/subscribers/unsubscribe-by-token
**Description**: Unsubscribe using unsubscribe token from email.
**Transition**: unsubscribe (ACTIVE/PENDING → UNSUBSCRIBED)

**Request Body**:
```json
{
    "unsubscribeToken": "550e8400-e29b-41d4-a716-446655440000",
    "transitionName": "unsubscribe"
}
```

**Response Body**:
```json
{
    "message": "Successfully unsubscribed",
    "email": "user@example.com"
}
```

### 5. GET /api/subscribers
**Description**: Get all subscribers (admin endpoint).

**Response Body**:
```json
{
    "subscribers": [
        {
            "id": 1,
            "email": "user@example.com",
            "firstName": "John",
            "lastName": "Doe",
            "subscriptionDate": "2024-01-15T10:30:00Z",
            "isActive": true,
            "state": "ACTIVE"
        }
    ],
    "totalCount": 1,
    "activeCount": 1
}
```

### 6. GET /api/subscribers/{id}
**Description**: Get subscriber by ID.

**Response Body**:
```json
{
    "id": 1,
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "subscriptionDate": "2024-01-15T10:30:00Z",
    "isActive": true,
    "state": "ACTIVE"
}
```

---

## CatFactRoutes

### 7. POST /api/catfacts/retrieve
**Description**: Manually trigger cat fact retrieval from external API.
**Transition**: Uses transition to move from INITIAL to RETRIEVED state.

**Request Body**:
```json
{
    "transitionName": null
}
```

**Response Body**:
```json
{
    "id": 1,
    "factText": "Cats have 32 muscles in each ear.",
    "factLength": 32,
    "retrievedDate": "2024-01-15T10:30:00Z",
    "state": "RETRIEVED"
}
```

### 8. PUT /api/catfacts/{id}/schedule
**Description**: Schedule a cat fact for weekly distribution.
**Transition**: schedule-fact (RETRIEVED → SCHEDULED)

**Request Body**:
```json
{
    "transitionName": "schedule-fact",
    "scheduledSendDate": "2024-01-22"
}
```

**Response Body**:
```json
{
    "id": 1,
    "factText": "Cats have 32 muscles in each ear.",
    "scheduledSendDate": "2024-01-22",
    "state": "SCHEDULED"
}
```

---

## EmailDeliveryRoutes

### 11. GET /api/email-deliveries
**Description**: Get all email deliveries with optional filters.

**Query Parameters**:
- `subscriberId` (optional): Filter by subscriber ID
- `catFactId` (optional): Filter by cat fact ID
- `state` (optional): Filter by state (PENDING, SENT, FAILED, DELIVERED)
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response Body**:
```json
{
    "emailDeliveries": [
        {
            "id": 1,
            "subscriberId": 1,
            "catFactId": 1,
            "sentDate": "2024-01-22T09:00:00Z",
            "deliveryAttempts": 1,
            "state": "SENT"
        }
    ],
    "totalCount": 1,
    "page": 0,
    "size": 20
}
```

### 12. PUT /api/email-deliveries/{id}/retry
**Description**: Retry a failed email delivery.
**Transition**: retry-delivery (FAILED → PENDING)

**Request Body**:
```json
{
    "transitionName": "retry-delivery"
}
```

**Response Body**:
```json
{
    "id": 1,
    "subscriberId": 1,
    "catFactId": 1,
    "deliveryAttempts": 2,
    "errorMessage": null,
    "state": "PENDING"
}
```

### 13. GET /api/email-deliveries/{id}
**Description**: Get email delivery by ID.

**Response Body**:
```json
{
    "id": 1,
    "subscriberId": 1,
    "catFactId": 1,
    "sentDate": "2024-01-22T09:00:00Z",
    "deliveryAttempts": 1,
    "lastAttemptDate": "2024-01-22T09:00:00Z",
    "errorMessage": null,
    "state": "SENT"
}
```

---

## InteractionRoutes

### 14. POST /api/interactions
**Description**: Record a user interaction with cat fact emails.
**Transition**: Uses transition to move from INITIAL to RECORDED state.

**Request Body**:
```json
{
    "subscriberId": 1,
    "emailDeliveryId": 1,
    "interactionType": "EMAIL_OPEN",
    "ipAddress": "192.168.1.1",
    "userAgent": "Mozilla/5.0...",
    "additionalData": "{\"timestamp\": \"2024-01-22T10:15:00Z\"}"
}
```

**Response Body**:
```json
{
    "id": 1,
    "subscriberId": 1,
    "emailDeliveryId": 1,
    "interactionType": "EMAIL_OPEN",
    "interactionDate": "2024-01-22T10:15:00Z",
    "state": "RECORDED"
}
```

### 15. GET /api/interactions
**Description**: Get all interactions with optional filters.

**Query Parameters**:
- `subscriberId` (optional): Filter by subscriber ID
- `emailDeliveryId` (optional): Filter by email delivery ID
- `interactionType` (optional): Filter by interaction type
- `startDate` (optional): Filter by start date
- `endDate` (optional): Filter by end date
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response Body**:
```json
{
    "interactions": [
        {
            "id": 1,
            "subscriberId": 1,
            "emailDeliveryId": 1,
            "interactionType": "EMAIL_OPEN",
            "interactionDate": "2024-01-22T10:15:00Z",
            "state": "PROCESSED"
        }
    ],
    "totalCount": 1,
    "page": 0,
    "size": 20
}
```

---

## WeeklyScheduleRoutes

### 16. POST /api/weekly-schedules
**Description**: Create a new weekly schedule.
**Transition**: Uses transition to move from INITIAL to CREATED state.

**Request Body**:
```json
{
    "weekStartDate": "2024-01-22"
}
```

**Response Body**:
```json
{
    "id": 1,
    "weekStartDate": "2024-01-22",
    "weekEndDate": "2024-01-28",
    "scheduledSendDate": "2024-01-22",
    "totalSubscribers": 150,
    "emailsSent": 0,
    "emailsFailed": 0,
    "state": "CREATED"
}
```

### 17. PUT /api/weekly-schedules/{id}/assign-fact
**Description**: Assign a cat fact to the weekly schedule.
**Transition**: assign-fact (CREATED → FACT_ASSIGNED)

**Request Body**:
```json
{
    "transitionName": "assign-fact"
}
```

**Response Body**:
```json
{
    "id": 1,
    "weekStartDate": "2024-01-22",
    "catFactId": 1,
    "state": "FACT_ASSIGNED"
}
```

### 18. PUT /api/weekly-schedules/{id}/send-emails
**Description**: Trigger email distribution for the weekly schedule.
**Transition**: send-emails (FACT_ASSIGNED → EMAILS_SENT)

**Request Body**:
```json
{
    "transitionName": "send-emails"
}
```

**Response Body**:
```json
{
    "id": 1,
    "weekStartDate": "2024-01-22",
    "catFactId": 1,
    "emailsSent": 148,
    "emailsFailed": 2,
    "state": "EMAILS_SENT"
}
```

### 19. PUT /api/weekly-schedules/{id}/complete
**Description**: Complete the weekly schedule and generate reports.
**Transition**: complete-schedule (EMAILS_SENT → COMPLETED)

**Request Body**:
```json
{
    "transitionName": "complete-schedule"
}
```

**Response Body**:
```json
{
    "id": 1,
    "weekStartDate": "2024-01-22",
    "emailsSent": 148,
    "emailsFailed": 2,
    "state": "COMPLETED"
}
```

### 20. GET /api/weekly-schedules
**Description**: Get all weekly schedules with optional filters.

**Query Parameters**:
- `state` (optional): Filter by state
- `startDate` (optional): Filter by week start date (from)
- `endDate` (optional): Filter by week start date (to)
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response Body**:
```json
{
    "weeklySchedules": [
        {
            "id": 1,
            "weekStartDate": "2024-01-22",
            "weekEndDate": "2024-01-28",
            "scheduledSendDate": "2024-01-22",
            "catFactId": 1,
            "totalSubscribers": 150,
            "emailsSent": 148,
            "emailsFailed": 2,
            "state": "COMPLETED"
        }
    ],
    "totalCount": 1,
    "page": 0,
    "size": 20
}
```

### 21. GET /api/weekly-schedules/{id}
**Description**: Get weekly schedule by ID.

**Response Body**:
```json
{
    "id": 1,
    "weekStartDate": "2024-01-22",
    "weekEndDate": "2024-01-28",
    "scheduledSendDate": "2024-01-22",
    "catFactId": 1,
    "totalSubscribers": 150,
    "emailsSent": 148,
    "emailsFailed": 2,
    "state": "COMPLETED"
}
```

---

## Reporting Routes

### 22. GET /api/reports/subscriber-stats
**Description**: Get subscriber statistics and analytics.

**Response Body**:
```json
{
    "totalSubscribers": 150,
    "activeSubscribers": 148,
    "pendingSubscribers": 2,
    "unsubscribedSubscribers": 25,
    "subscriptionsThisWeek": 5,
    "subscriptionsThisMonth": 20,
    "unsubscribesThisWeek": 1,
    "unsubscribesThisMonth": 3
}
```

### 23. GET /api/reports/email-stats
**Description**: Get email delivery statistics.

**Query Parameters**:
- `startDate` (optional): Start date for statistics
- `endDate` (optional): End date for statistics

**Response Body**:
```json
{
    "totalEmailsSent": 1480,
    "totalEmailsFailed": 20,
    "successRate": 98.65,
    "averageEmailsPerWeek": 148,
    "interactionStats": {
        "totalOpens": 890,
        "totalClicks": 45,
        "openRate": 60.14,
        "clickRate": 3.04
    }
}
```

### 24. GET /api/reports/cat-fact-stats
**Description**: Get cat fact statistics and performance.

**Response Body**:
```json
{
    "totalFactsRetrieved": 52,
    "totalFactsSent": 50,
    "averageFactLength": 85,
    "mostPopularFact": {
        "id": 15,
        "factText": "Cats have 32 muscles in each ear.",
        "opens": 145,
        "clicks": 12
    }
}
```

### 9. GET /api/catfacts
**Description**: Get all cat facts with optional state filter.

**Query Parameters**:
- `state` (optional): Filter by state (RETRIEVED, SCHEDULED, SENT, ARCHIVED)
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response Body**:
```json
{
    "catFacts": [
        {
            "id": 1,
            "factText": "Cats have 32 muscles in each ear.",
            "factLength": 32,
            "retrievedDate": "2024-01-15T10:30:00Z",
            "scheduledSendDate": "2024-01-22",
            "state": "SCHEDULED"
        }
    ],
    "totalCount": 1,
    "page": 0,
    "size": 20
}
```

### 10. GET /api/catfacts/{id}
**Description**: Get cat fact by ID.

**Response Body**:
```json
{
    "id": 1,
    "factText": "Cats have 32 muscles in each ear.",
    "factLength": 32,
    "retrievedDate": "2024-01-15T10:30:00Z",
    "scheduledSendDate": "2024-01-22",
    "state": "SCHEDULED"
}
```
