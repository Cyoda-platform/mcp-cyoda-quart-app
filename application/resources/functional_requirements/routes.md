# Routes

## SubscriberRoutes

### POST /api/subscribers
**Description:** Create a new subscriber (sign up for weekly cat facts)
**Transition:** null (triggers initial → pending transition automatically)

**Request:**
```json
{
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe"
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "subscriptionDate": "2024-01-15T10:30:00Z",
    "isActive": false,
    "state": "pending"
}
```

### GET /api/subscribers/{id}
**Description:** Get subscriber details by ID

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "subscriptionDate": "2024-01-15T10:30:00Z",
    "isActive": true,
    "state": "active"
}
```

### PUT /api/subscribers/{id}
**Description:** Update subscriber information
**Transition:** null (no state change)

**Request:**
```json
{
    "firstName": "Jane",
    "lastName": "Smith",
    "transitionName": null
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "firstName": "Jane",
    "lastName": "Smith",
    "subscriptionDate": "2024-01-15T10:30:00Z",
    "isActive": true,
    "state": "active"
}
```

### PUT /api/subscribers/{id}/activate
**Description:** Activate a pending subscriber
**Transition:** "pending_to_active"

**Request:**
```json
{
    "transitionName": "pending_to_active"
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "isActive": true,
    "state": "active"
}
```

### PUT /api/subscribers/{id}/unsubscribe
**Description:** Unsubscribe a subscriber
**Transition:** "active_to_unsubscribed"

**Request:**
```json
{
    "transitionName": "active_to_unsubscribed"
}
```

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "isActive": false,
    "state": "unsubscribed"
}
```

### GET /api/subscribers/unsubscribe/{token}
**Description:** Unsubscribe via email link using unsubscribe token
**Transition:** "active_to_unsubscribed"

**Response:**
```json
{
    "message": "Successfully unsubscribed",
    "email": "user@example.com"
}
```

### GET /api/subscribers
**Description:** Get all subscribers with optional filtering

**Query Parameters:**
- `state` (optional): Filter by state (active, pending, unsubscribed, bounced)
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response:**
```json
{
    "content": [
        {
            "id": 1,
            "email": "user@example.com",
            "firstName": "John",
            "lastName": "Doe",
            "isActive": true,
            "state": "active"
        }
    ],
    "totalElements": 1,
    "totalPages": 1,
    "size": 20,
    "number": 0
}
```

---

## CatFactRoutes

### POST /api/catfacts
**Description:** Manually trigger cat fact retrieval
**Transition:** null (triggers initial → retrieved transition automatically)

**Request:**
```json
{}
```

**Response:**
```json
{
    "id": 1,
    "fact": "Cats have 32 muscles in each ear.",
    "length": 32,
    "retrievedDate": "2024-01-15T10:30:00Z",
    "state": "retrieved"
}
```

### GET /api/catfacts/{id}
**Description:** Get cat fact details by ID

**Response:**
```json
{
    "id": 1,
    "fact": "Cats have 32 muscles in each ear.",
    "length": 32,
    "retrievedDate": "2024-01-15T10:30:00Z",
    "scheduledSendDate": "2024-01-22T09:00:00Z",
    "state": "scheduled"
}
```

### PUT /api/catfacts/{id}/schedule
**Description:** Schedule cat fact for distribution
**Transition:** "retrieved_to_scheduled"

**Request:**
```json
{
    "scheduledSendDate": "2024-01-22T09:00:00Z",
    "transitionName": "retrieved_to_scheduled"
}
```

**Response:**
```json
{
    "id": 1,
    "fact": "Cats have 32 muscles in each ear.",
    "scheduledSendDate": "2024-01-22T09:00:00Z",
    "state": "scheduled"
}
```

### PUT /api/catfacts/{id}/distribute
**Description:** Distribute cat fact to subscribers
**Transition:** "scheduled_to_sent"

**Request:**
```json
{
    "transitionName": "scheduled_to_sent"
}
```

**Response:**
```json
{
    "id": 1,
    "fact": "Cats have 32 muscles in each ear.",
    "state": "sent",
    "distributionCount": 150
}
```

### GET /api/catfacts
**Description:** Get all cat facts with optional filtering

**Query Parameters:**
- `state` (optional): Filter by state (retrieved, scheduled, sent, archived)
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response:**
```json
{
    "content": [
        {
            "id": 1,
            "fact": "Cats have 32 muscles in each ear.",
            "length": 32,
            "retrievedDate": "2024-01-15T10:30:00Z",
            "state": "archived"
        }
    ],
    "totalElements": 1,
    "totalPages": 1
}
```

---

## EmailDeliveryRoutes

### GET /api/email-deliveries/{id}
**Description:** Get email delivery details by ID

**Response:**
```json
{
    "id": 1,
    "subscriberId": 1,
    "catFactId": 1,
    "sentDate": "2024-01-22T09:15:00Z",
    "deliveryAttempts": 1,
    "opened": true,
    "openedDate": "2024-01-22T10:30:00Z",
    "state": "opened"
}
```

### PUT /api/email-deliveries/{id}/retry
**Description:** Retry failed email delivery
**Transition:** "failed_to_pending"

**Request:**
```json
{
    "transitionName": "failed_to_pending"
}
```

**Response:**
```json
{
    "id": 1,
    "subscriberId": 1,
    "catFactId": 1,
    "deliveryAttempts": 2,
    "state": "pending"
}
```

### PUT /api/email-deliveries/{id}/mark-opened
**Description:** Mark email as opened (tracking endpoint)
**Transition:** "delivered_to_opened"

**Request:**
```json
{
    "transitionName": "delivered_to_opened"
}
```

**Response:**
```json
{
    "id": 1,
    "opened": true,
    "openedDate": "2024-01-22T10:30:00Z",
    "state": "opened"
}
```

### GET /api/email-deliveries
**Description:** Get email deliveries with filtering

**Query Parameters:**
- `subscriberId` (optional): Filter by subscriber ID
- `catFactId` (optional): Filter by cat fact ID
- `state` (optional): Filter by state (pending, sent, delivered, opened, failed, bounced)
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response:**
```json
{
    "content": [
        {
            "id": 1,
            "subscriberId": 1,
            "catFactId": 1,
            "sentDate": "2024-01-22T09:15:00Z",
            "opened": true,
            "state": "opened"
        }
    ],
    "totalElements": 1,
    "totalPages": 1
}
```

---

## WeeklyScheduleRoutes

### POST /api/weekly-schedules
**Description:** Create a new weekly schedule
**Transition:** null (triggers initial → created transition automatically)

**Request:**
```json
{
    "weekStartDate": "2024-01-15",
    "scheduledDate": "2024-01-22T09:00:00Z"
}
```

**Response:**
```json
{
    "id": 1,
    "weekStartDate": "2024-01-15",
    "weekEndDate": "2024-01-21",
    "scheduledDate": "2024-01-22T09:00:00Z",
    "subscriberCount": 150,
    "state": "created"
}
```

### GET /api/weekly-schedules/{id}
**Description:** Get weekly schedule details by ID

**Response:**
```json
{
    "id": 1,
    "weekStartDate": "2024-01-15",
    "weekEndDate": "2024-01-21",
    "catFactId": 1,
    "scheduledDate": "2024-01-22T09:00:00Z",
    "executedDate": "2024-01-22T09:15:00Z",
    "subscriberCount": 150,
    "state": "completed"
}
```

### PUT /api/weekly-schedules/{id}/execute
**Description:** Manually execute weekly schedule
**Transition:** "created_to_fact_retrieved"

**Request:**
```json
{
    "transitionName": "created_to_fact_retrieved"
}
```

**Response:**
```json
{
    "id": 1,
    "catFactId": 1,
    "state": "fact_retrieved"
}
```

### GET /api/weekly-schedules
**Description:** Get all weekly schedules

**Query Parameters:**
- `state` (optional): Filter by state (created, fact_retrieved, emails_sent, completed)
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response:**
```json
{
    "content": [
        {
            "id": 1,
            "weekStartDate": "2024-01-15",
            "weekEndDate": "2024-01-21",
            "subscriberCount": 150,
            "state": "completed"
        }
    ],
    "totalElements": 1,
    "totalPages": 1
}
```

---

## ReportingRoutes

### GET /api/reports/subscribers
**Description:** Get subscriber statistics

**Response:**
```json
{
    "totalSubscribers": 150,
    "activeSubscribers": 145,
    "pendingSubscribers": 3,
    "unsubscribedSubscribers": 2,
    "bouncedSubscribers": 0,
    "subscriptionsThisWeek": 5,
    "subscriptionsThisMonth": 23
}
```

### GET /api/reports/email-deliveries
**Description:** Get email delivery statistics

**Query Parameters:**
- `startDate` (optional): Start date for statistics
- `endDate` (optional): End date for statistics

**Response:**
```json
{
    "totalEmailsSent": 1450,
    "successfulDeliveries": 1420,
    "failedDeliveries": 30,
    "emailsOpened": 850,
    "openRate": 59.9,
    "bounceRate": 2.1,
    "deliveryRate": 97.9
}
```

### GET /api/reports/cat-facts
**Description:** Get cat fact distribution statistics

**Response:**
```json
{
    "totalFactsRetrieved": 10,
    "factsDistributed": 8,
    "averageFactLength": 45,
    "lastDistributionDate": "2024-01-22T09:00:00Z",
    "nextScheduledDistribution": "2024-01-29T09:00:00Z"
}
```
