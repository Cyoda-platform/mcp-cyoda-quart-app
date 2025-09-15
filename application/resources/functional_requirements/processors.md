# Processors

## 1. Subscriber Processors

### SubscriberRegistrationProcessor

**Entity:** Subscriber
**Input Data:** Email, firstName (optional), lastName (optional)
**Description:** Handles new subscriber registration and sends confirmation email.

**Expected Entity Output:**
- Updates Subscriber entity with registration details
- Sets isActive to false
- Generates confirmationToken and unsubscribeToken
- Sets subscriptionDate to current timestamp
- Transition: INITIAL → PENDING_CONFIRMATION

**Pseudocode:**
```
process(subscriberEntity, inputData):
    1. Validate email format and uniqueness
    2. Set subscriber.email = inputData.email
    3. Set subscriber.firstName = inputData.firstName (if provided)
    4. Set subscriber.lastName = inputData.lastName (if provided)
    5. Set subscriber.subscriptionDate = current timestamp
    6. Set subscriber.isActive = false
    7. Generate unique confirmationToken (UUID)
    8. Generate unique unsubscribeToken (UUID)
    9. Set subscriber.confirmationToken = confirmationToken
    10. Set subscriber.unsubscribeToken = unsubscribeToken
    11. Send confirmation email with confirmation link
    12. Return updated subscriber entity
```

### SubscriberConfirmationProcessor

**Entity:** Subscriber
**Input Data:** confirmationToken
**Description:** Confirms subscriber email and activates subscription.

**Expected Entity Output:**
- Updates Subscriber entity to active status
- Sets isActive to true
- Clears confirmationToken
- Sets confirmedAt timestamp
- Transition: PENDING_CONFIRMATION → ACTIVE

**Pseudocode:**
```
process(subscriberEntity, inputData):
    1. Validate confirmationToken matches subscriber.confirmationToken
    2. Check if token is not expired (within 24 hours)
    3. Set subscriber.isActive = true
    4. Set subscriber.confirmedAt = current timestamp
    5. Clear subscriber.confirmationToken = null
    6. Send welcome email to subscriber
    7. Return updated subscriber entity
```

### SubscriberUnsubscribeProcessor

**Entity:** Subscriber
**Input Data:** unsubscribeToken
**Description:** Handles subscriber unsubscription.

**Expected Entity Output:**
- Updates Subscriber entity to unsubscribed status
- Sets isActive to false
- Transition: ACTIVE → UNSUBSCRIBED or PENDING_CONFIRMATION → UNSUBSCRIBED

**Pseudocode:**
```
process(subscriberEntity, inputData):
    1. Validate unsubscribeToken matches subscriber.unsubscribeToken
    2. Set subscriber.isActive = false
    3. Send unsubscribe confirmation email
    4. Record unsubscribe interaction (create SubscriberInteraction with type UNSUBSCRIBED)
    5. Return updated subscriber entity
```

---

## 2. CatFact Processors

### CatFactRetrievalProcessor

**Entity:** CatFact
**Input Data:** None (scheduled trigger)
**Description:** Retrieves a new cat fact from the external API.

**Expected Entity Output:**
- Creates new CatFact entity with retrieved data
- Transition: INITIAL → RETRIEVED

**Pseudocode:**
```
process(catFactEntity, inputData):
    1. Call Cat Fact API (https://catfact.ninja/fact)
    2. Parse API response to extract fact text and external ID
    3. Set catFact.factText = API response fact
    4. Set catFact.externalId = API response ID (if available)
    5. Set catFact.retrievedAt = current timestamp
    6. Set catFact.source = "catfact.ninja"
    7. Return updated catFact entity
```

### CatFactSchedulingProcessor

**Entity:** CatFact
**Input Data:** None
**Description:** Schedules cat fact for next weekly distribution.

**Expected Entity Output:**
- Updates CatFact entity with scheduling information
- Transition: RETRIEVED → SCHEDULED

**Pseudocode:**
```
process(catFactEntity, inputData):
    1. Calculate next Monday as scheduled send date
    2. Set catFact.scheduledSendDate = next Monday
    3. Return updated catFact entity
```

### CatFactDistributionProcessor

**Entity:** CatFact
**Input Data:** None
**Description:** Distributes cat fact to all active subscribers via email campaign.

**Expected Entity Output:**
- Updates CatFact entity with sent timestamp
- Creates EmailCampaign entity (transition: INITIAL → SCHEDULED)
- Transition: SCHEDULED → SENT

**Pseudocode:**
```
process(catFactEntity, inputData):
    1. Get all active subscribers (isActive = true)
    2. Create new EmailCampaign entity
    3. Set emailCampaign.catFactId = catFactEntity.id
    4. Set emailCampaign.campaignDate = current date
    5. Set emailCampaign.scheduledAt = current timestamp
    6. Set emailCampaign.totalSubscribers = count of active subscribers
    7. Set emailCampaign.subject = "Your Weekly Cat Fact"
    8. Trigger EmailCampaign workflow (transition to SCHEDULED)
    9. Set catFact.sentAt = current timestamp
    10. Return updated catFact entity
```

### CatFactRetryProcessor

**Entity:** CatFact
**Input Data:** None
**Description:** Retries sending a failed cat fact.

**Expected Entity Output:**
- Resets CatFact for retry
- Transition: FAILED → SCHEDULED

**Pseudocode:**
```
process(catFactEntity, inputData):
    1. Clear catFact.sentAt = null
    2. Update catFact.scheduledSendDate = current date
    3. Return updated catFact entity
```

---

## 3. SubscriberInteraction Processors

### SubscriberInteractionRecordingProcessor

**Entity:** SubscriberInteraction
**Input Data:** subscriberId, catFactId, interactionType, emailDeliveryStatus (optional), userAgent (optional), ipAddress (optional)
**Description:** Records a new subscriber interaction.

**Expected Entity Output:**
- Creates new SubscriberInteraction entity
- Transition: INITIAL → RECORDED

**Pseudocode:**
```
process(interactionEntity, inputData):
    1. Set interaction.subscriberId = inputData.subscriberId
    2. Set interaction.catFactId = inputData.catFactId
    3. Set interaction.interactionType = inputData.interactionType
    4. Set interaction.interactionDate = current timestamp
    5. Set interaction.emailDeliveryStatus = inputData.emailDeliveryStatus (if provided)
    6. Set interaction.userAgent = inputData.userAgent (if provided)
    7. Set interaction.ipAddress = inputData.ipAddress (if provided)
    8. Return updated interaction entity
```

### SubscriberInteractionProcessingProcessor

**Entity:** SubscriberInteraction
**Input Data:** None
**Description:** Processes interaction for analytics and reporting.

**Expected Entity Output:**
- Updates interaction processing status
- Updates analytics/reporting data
- Transition: RECORDED → PROCESSED

**Pseudocode:**
```
process(interactionEntity, inputData):
    1. Update analytics counters based on interaction type
    2. If interaction type is EMAIL_OPENED, increment open rate metrics
    3. If interaction type is EMAIL_CLICKED, increment click rate metrics
    4. If interaction type is UNSUBSCRIBED, increment unsubscribe rate metrics
    5. Update subscriber engagement score
    6. Return updated interaction entity
```

---

## 4. EmailCampaign Processors

### EmailCampaignSchedulingProcessor

**Entity:** EmailCampaign
**Input Data:** catFactId, campaignDate
**Description:** Schedules a new email campaign.

**Expected Entity Output:**
- Updates EmailCampaign entity with scheduling details
- Transition: INITIAL → SCHEDULED

**Pseudocode:**
```
process(campaignEntity, inputData):
    1. Set campaign.catFactId = inputData.catFactId
    2. Set campaign.campaignDate = inputData.campaignDate
    3. Set campaign.scheduledAt = current timestamp
    4. Get count of active subscribers
    5. Set campaign.totalSubscribers = active subscriber count
    6. Set campaign.subject = "Your Weekly Cat Fact"
    7. Set campaign.templateVersion = current template version
    8. Return updated campaign entity
```

### EmailCampaignExecutionProcessor

**Entity:** EmailCampaign
**Input Data:** None
**Description:** Executes the email campaign by sending emails to all subscribers.

**Expected Entity Output:**
- Updates EmailCampaign entity with execution details
- Creates SubscriberInteraction entities for each email sent
- Transition: SCHEDULED → IN_PROGRESS

**Pseudocode:**
```
process(campaignEntity, inputData):
    1. Set campaign.startedAt = current timestamp
    2. Get cat fact by campaign.catFactId
    3. Get all active subscribers
    4. Initialize emailsSent = 0, emailsFailed = 0
    5. For each active subscriber:
        a. Compose email with cat fact content
        b. Send email to subscriber
        c. If email sent successfully:
            - Increment emailsSent
            - Create SubscriberInteraction (type: EMAIL_SENT, transition: null)
        d. If email failed:
            - Increment emailsFailed
            - Create SubscriberInteraction (type: EMAIL_FAILED, transition: null)
    6. Set campaign.emailsSent = emailsSent
    7. Set campaign.emailsFailed = emailsFailed
    8. Return updated campaign entity
```

### EmailCampaignCompletionProcessor

**Entity:** EmailCampaign
**Input Data:** None
**Description:** Completes the email campaign execution.

**Expected Entity Output:**
- Updates EmailCampaign entity with completion timestamp
- Transition: IN_PROGRESS → COMPLETED

**Pseudocode:**
```
process(campaignEntity, inputData):
    1. Set campaign.completedAt = current timestamp
    2. Log campaign completion statistics
    3. Return updated campaign entity
```

### EmailCampaignRetryProcessor

**Entity:** EmailCampaign
**Input Data:** None
**Description:** Retries a failed email campaign.

**Expected Entity Output:**
- Resets EmailCampaign for retry
- Transition: FAILED → SCHEDULED

**Pseudocode:**
```
process(campaignEntity, inputData):
    1. Clear campaign.startedAt = null
    2. Clear campaign.completedAt = null
    3. Reset campaign.emailsSent = 0
    4. Reset campaign.emailsFailed = 0
    5. Set campaign.scheduledAt = current timestamp
    6. Return updated campaign entity
```
