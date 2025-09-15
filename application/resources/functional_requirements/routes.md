# Routes

## 1. SubscriberRoutes

**Class Name:** SubscriberRoutes

### POST /api/subscribers/subscribe

**Description:** Subscribe a new user to weekly cat facts.

**Request Body:**
```json
{
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Subscription successful. Please check your email to confirm.",
  "subscriberId": 123
}
```

**Transition:** INITIAL → PENDING_CONFIRMATION (via SubscriberRegistrationProcessor)

---

### GET /api/subscribers/confirm/{confirmationToken}

**Description:** Confirm subscriber email address.

**Path Parameters:**
- `confirmationToken` (String): The confirmation token sent via email

**Response Body:**
```json
{
  "success": true,
  "message": "Email confirmed successfully. You will now receive weekly cat facts!"
}
```

**Transition:** PENDING_CONFIRMATION → ACTIVE (via SubscriberConfirmationProcessor)

---

### GET /api/subscribers/unsubscribe/{unsubscribeToken}

**Description:** Unsubscribe from weekly cat facts.

**Path Parameters:**
- `unsubscribeToken` (String): The unsubscribe token

**Response Body:**
```json
{
  "success": true,
  "message": "You have been successfully unsubscribed from weekly cat facts."
}
```

**Transition:** ACTIVE → UNSUBSCRIBED or PENDING_CONFIRMATION → UNSUBSCRIBED (via SubscriberUnsubscribeProcessor)

---

### GET /api/subscribers/{subscriberId}

**Description:** Get subscriber details by ID.

**Path Parameters:**
- `subscriberId` (Long): The subscriber ID

**Response Body:**
```json
{
  "id": 123,
  "email": "user@example.com",
  "firstName": "John",
  "lastName": "Doe",
  "subscriptionDate": "2024-01-15T10:30:00Z",
  "isActive": true,
  "state": "ACTIVE"
}
```

**Transition:** null (read-only operation)

---

### PUT /api/subscribers/{subscriberId}

**Description:** Update subscriber information.

**Path Parameters:**
- `subscriberId` (Long): The subscriber ID

**Query Parameters:**
- `transitionName` (String, optional): null (no state change for profile updates)

**Request Body:**
```json
{
  "firstName": "Jane",
  "lastName": "Smith"
}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Subscriber information updated successfully.",
  "subscriber": {
    "id": 123,
    "email": "user@example.com",
    "firstName": "Jane",
    "lastName": "Smith"
  }
}
```

**Transition:** null (no state change)

---

## 2. CatFactRoutes

**Class Name:** CatFactRoutes

### POST /api/catfacts/retrieve

**Description:** Manually trigger cat fact retrieval from external API.

**Request Body:**
```json
{
  "source": "catfact.ninja"
}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Cat fact retrieved successfully.",
  "catFact": {
    "id": 456,
    "factText": "Cats have 32 muscles in each ear.",
    "retrievedAt": "2024-01-15T10:30:00Z"
  }
}
```

**Transition:** INITIAL → RETRIEVED (via CatFactRetrievalProcessor)

---

### GET /api/catfacts/{catFactId}

**Description:** Get cat fact details by ID.

**Path Parameters:**
- `catFactId` (Long): The cat fact ID

**Response Body:**
```json
{
  "id": 456,
  "factText": "Cats have 32 muscles in each ear.",
  "externalId": "ext123",
  "retrievedAt": "2024-01-15T10:30:00Z",
  "scheduledSendDate": "2024-01-22",
  "sentAt": null,
  "source": "catfact.ninja",
  "state": "SCHEDULED"
}
```

**Transition:** null (read-only operation)

---

### PUT /api/catfacts/{catFactId}/schedule

**Description:** Schedule a cat fact for distribution.

**Path Parameters:**
- `catFactId` (Long): The cat fact ID

**Query Parameters:**
- `transitionName` (String): "RETRIEVED_TO_SCHEDULED"

**Request Body:**
```json
{
  "scheduledSendDate": "2024-01-22"
}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Cat fact scheduled successfully."
}
```

**Transition:** RETRIEVED → SCHEDULED (via CatFactSchedulingProcessor)

---

### POST /api/catfacts/{catFactId}/distribute

**Description:** Manually trigger cat fact distribution.

**Path Parameters:**
- `catFactId` (Long): The cat fact ID

**Query Parameters:**
- `transitionName` (String): "SCHEDULED_TO_SENT"

**Request Body:**
```json
{}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Cat fact distribution initiated.",
  "campaignId": 789
}
```

**Transition:** SCHEDULED → SENT (via CatFactDistributionProcessor)

---

### POST /api/catfacts/{catFactId}/retry

**Description:** Retry sending a failed cat fact.

**Path Parameters:**
- `catFactId` (Long): The cat fact ID

**Query Parameters:**
- `transitionName` (String): "FAILED_TO_SCHEDULED"

**Request Body:**
```json
{}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Cat fact retry scheduled successfully."
}
```

**Transition:** FAILED → SCHEDULED (via CatFactRetryProcessor)

---

### GET /api/catfacts

**Description:** Get list of cat facts with filtering options.

**Query Parameters:**
- `state` (String, optional): Filter by state (RETRIEVED, SCHEDULED, SENT, FAILED)
- `page` (Integer, optional): Page number (default: 0)
- `size` (Integer, optional): Page size (default: 20)

**Response Body:**
```json
{
  "content": [
    {
      "id": 456,
      "factText": "Cats have 32 muscles in each ear.",
      "state": "SCHEDULED",
      "scheduledSendDate": "2024-01-22"
    }
  ],
  "totalElements": 1,
  "totalPages": 1,
  "page": 0,
  "size": 20
}
```

**Transition:** null (read-only operation)

---

## 3. EmailCampaignRoutes

**Class Name:** EmailCampaignRoutes

### POST /api/campaigns/schedule

**Description:** Schedule a new email campaign.

**Request Body:**
```json
{
  "catFactId": 456,
  "campaignDate": "2024-01-22"
}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Email campaign scheduled successfully.",
  "campaign": {
    "id": 789,
    "catFactId": 456,
    "campaignDate": "2024-01-22",
    "totalSubscribers": 150
  }
}
```

**Transition:** INITIAL → SCHEDULED (via EmailCampaignSchedulingProcessor)

---

### POST /api/campaigns/{campaignId}/execute

**Description:** Execute a scheduled email campaign.

**Path Parameters:**
- `campaignId` (Long): The campaign ID

**Query Parameters:**
- `transitionName` (String): "SCHEDULED_TO_IN_PROGRESS"

**Request Body:**
```json
{}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Email campaign execution started."
}
```

**Transition:** SCHEDULED → IN_PROGRESS (via EmailCampaignExecutionProcessor)

---

### GET /api/campaigns/{campaignId}

**Description:** Get campaign details by ID.

**Path Parameters:**
- `campaignId` (Long): The campaign ID

**Response Body:**
```json
{
  "id": 789,
  "catFactId": 456,
  "campaignDate": "2024-01-22",
  "scheduledAt": "2024-01-22T08:00:00Z",
  "startedAt": "2024-01-22T09:00:00Z",
  "completedAt": "2024-01-22T09:30:00Z",
  "totalSubscribers": 150,
  "emailsSent": 148,
  "emailsFailed": 2,
  "subject": "Your Weekly Cat Fact",
  "state": "COMPLETED"
}
```

**Transition:** null (read-only operation)

---

### POST /api/campaigns/{campaignId}/retry

**Description:** Retry a failed email campaign.

**Path Parameters:**
- `campaignId` (Long): The campaign ID

**Query Parameters:**
- `transitionName` (String): "FAILED_TO_SCHEDULED"

**Request Body:**
```json
{}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Email campaign retry scheduled successfully."
}
```

**Transition:** FAILED → SCHEDULED (via EmailCampaignRetryProcessor)

---

### GET /api/campaigns

**Description:** Get list of email campaigns with filtering options.

**Query Parameters:**
- `state` (String, optional): Filter by state (SCHEDULED, IN_PROGRESS, COMPLETED, FAILED)
- `startDate` (String, optional): Filter campaigns from this date (ISO format)
- `endDate` (String, optional): Filter campaigns to this date (ISO format)
- `page` (Integer, optional): Page number (default: 0)
- `size` (Integer, optional): Page size (default: 20)

**Response Body:**
```json
{
  "content": [
    {
      "id": 789,
      "campaignDate": "2024-01-22",
      "state": "COMPLETED",
      "totalSubscribers": 150,
      "emailsSent": 148,
      "emailsFailed": 2
    }
  ],
  "totalElements": 1,
  "totalPages": 1,
  "page": 0,
  "size": 20
}
```

**Transition:** null (read-only operation)

---

## 4. SubscriberInteractionRoutes

**Class Name:** SubscriberInteractionRoutes

### POST /api/interactions/record

**Description:** Record a subscriber interaction (email opened, clicked, etc.).

**Request Body:**
```json
{
  "subscriberId": 123,
  "catFactId": 456,
  "interactionType": "EMAIL_OPENED",
  "emailDeliveryStatus": "DELIVERED",
  "userAgent": "Mozilla/5.0...",
  "ipAddress": "192.168.1.1"
}
```

**Response Body:**
```json
{
  "success": true,
  "message": "Interaction recorded successfully.",
  "interactionId": 999
}
```

**Transition:** INITIAL → RECORDED (via SubscriberInteractionRecordingProcessor)

---

### GET /api/interactions/subscriber/{subscriberId}

**Description:** Get interactions for a specific subscriber.

**Path Parameters:**
- `subscriberId` (Long): The subscriber ID

**Query Parameters:**
- `page` (Integer, optional): Page number (default: 0)
- `size` (Integer, optional): Page size (default: 20)

**Response Body:**
```json
{
  "content": [
    {
      "id": 999,
      "catFactId": 456,
      "interactionType": "EMAIL_OPENED",
      "interactionDate": "2024-01-22T10:15:00Z",
      "emailDeliveryStatus": "DELIVERED"
    }
  ],
  "totalElements": 1,
  "totalPages": 1
}
```

**Transition:** null (read-only operation)

---

### GET /api/interactions/analytics

**Description:** Get analytics and reporting data for subscriber interactions.

**Query Parameters:**
- `startDate` (String, optional): Start date for analytics (ISO format)
- `endDate` (String, optional): End date for analytics (ISO format)
- `interactionType` (String, optional): Filter by interaction type

**Response Body:**
```json
{
  "totalInteractions": 1500,
  "emailsSent": 1200,
  "emailsOpened": 800,
  "emailsClicked": 200,
  "unsubscribes": 50,
  "openRate": 0.67,
  "clickRate": 0.17,
  "unsubscribeRate": 0.04
}
```

**Transition:** null (read-only operation)
