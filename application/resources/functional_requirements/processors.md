# Processors

## Subscriber Processors

### SubscriberRegistrationProcessor

**Entity:** Subscriber
**Input:** Subscriber entity with email, firstName, lastName
**Description:** Processes new subscriber registration
**Output:** Subscriber entity with generated ID, subscription date, unsubscribe token, and isActive set to true

**Pseudocode:**
```
process(subscriber):
    validate email format
    check if email already exists in database
    if email exists and is active:
        throw exception "Email already subscribed"
    if email exists and is inactive:
        reactivate existing subscriber
        return existing subscriber
    generate unique unsubscribe token
    set subscription date to current timestamp
    set isActive to true
    save subscriber to database
    return subscriber
```

### SubscriberActivationProcessor

**Entity:** Subscriber
**Input:** Subscriber entity in PENDING state
**Description:** Activates a pending subscriber
**Output:** Subscriber entity ready to receive emails

**Pseudocode:**
```
process(subscriber):
    validate subscriber is in PENDING state
    set isActive to true
    update subscriber in database
    log activation event
    return subscriber
```

### SubscriberUnsubscribeProcessor

**Entity:** Subscriber
**Input:** Subscriber entity with unsubscribe token
**Description:** Processes subscriber unsubscription
**Output:** Subscriber entity with isActive set to false
**Transition:** null (state managed by workflow)

**Pseudocode:**
```
process(subscriber):
    validate unsubscribe token
    set isActive to false
    update subscriber in database
    create SubscriberInteraction with type UNSUBSCRIBED
    trigger SubscriberInteractionWorkflow with transition "INITIAL"
    log unsubscription event
    return subscriber
```

### SubscriberBounceProcessor

**Entity:** Subscriber
**Input:** Subscriber entity and bounce information
**Description:** Processes email bounce for subscriber
**Output:** Subscriber entity marked as bounced

**Pseudocode:**
```
process(subscriber):
    set isActive to false
    update subscriber in database
    create SubscriberInteraction with type EMAIL_BOUNCED
    trigger SubscriberInteractionWorkflow with transition "INITIAL"
    log bounce event with bounce reason
    return subscriber
```

### SubscriberReactivationProcessor

**Entity:** Subscriber
**Input:** Subscriber entity in BOUNCED state
**Description:** Reactivates a bounced subscriber
**Output:** Subscriber entity reactivated for email delivery

**Pseudocode:**
```
process(subscriber):
    validate subscriber is in BOUNCED state
    set isActive to true
    update subscriber in database
    log reactivation event
    return subscriber
```

## CatFact Processors

### CatFactRetrievalProcessor

**Entity:** CatFact
**Input:** Empty CatFact entity
**Description:** Retrieves cat fact from external API
**Output:** CatFact entity with fact text and metadata

**Pseudocode:**
```
process(catFact):
    call external Cat Fact API (https://catfact.ninja/fact)
    if API call fails:
        throw exception "Failed to retrieve cat fact"
    extract fact text and length from API response
    set retrievedDate to current timestamp
    set externalApiId if available in response
    save catFact to database
    return catFact
```

### CatFactSchedulingProcessor

**Entity:** CatFact
**Input:** CatFact entity in RETRIEVED state
**Description:** Schedules cat fact for weekly distribution
**Output:** CatFact entity with scheduled send date

**Pseudocode:**
```
process(catFact):
    calculate next weekly send date (e.g., every Monday at 9 AM)
    set scheduledSendDate
    update catFact in database
    create EmailCampaign entity with this catFact
    trigger EmailCampaignWorkflow with transition "INITIAL"
    return catFact
```

### CatFactDistributionProcessor

**Entity:** CatFact
**Input:** CatFact entity in SCHEDULED state
**Description:** Distributes cat fact to all active subscribers
**Output:** CatFact entity with actual send date

**Pseudocode:**
```
process(catFact):
    get all active subscribers from database
    if no active subscribers:
        log warning "No active subscribers found"
        set actualSendDate to current timestamp
        return catFact
    
    for each active subscriber:
        send email with cat fact
        create SubscriberInteraction with type EMAIL_SENT
        trigger SubscriberInteractionWorkflow with transition "INITIAL"
    
    set actualSendDate to current timestamp
    update catFact in database
    return catFact
```

### CatFactRetryProcessor

**Entity:** CatFact
**Input:** CatFact entity in FAILED state
**Description:** Retries failed cat fact distribution
**Output:** CatFact entity ready for retry

**Pseudocode:**
```
process(catFact):
    validate catFact is in FAILED state
    reset actualSendDate to null
    update catFact in database
    log retry attempt
    return catFact
```

## SubscriberInteraction Processors

### SubscriberInteractionRecordProcessor

**Entity:** SubscriberInteraction
**Input:** SubscriberInteraction entity with basic data
**Description:** Records subscriber interaction in the system
**Output:** SubscriberInteraction entity with complete data

**Pseudocode:**
```
process(interaction):
    validate subscriberId exists
    validate catFactId exists (if applicable)
    set interactionDate to current timestamp
    save interaction to database
    return interaction
```

### SubscriberInteractionProcessingProcessor

**Entity:** SubscriberInteraction
**Input:** SubscriberInteraction entity in RECORDED state
**Description:** Processes interaction for reporting and analytics
**Output:** SubscriberInteraction entity ready for reporting

**Pseudocode:**
```
process(interaction):
    update reporting metrics based on interaction type
    if interaction type is EMAIL_OPENED:
        increment email open rate metrics
    if interaction type is EMAIL_CLICKED:
        increment email click rate metrics
    if interaction type is UNSUBSCRIBED:
        update churn rate metrics
    
    update interaction in database
    return interaction
```

## EmailCampaign Processors

### EmailCampaignSchedulingProcessor

**Entity:** EmailCampaign
**Input:** EmailCampaign entity with catFactId
**Description:** Schedules email campaign for execution
**Output:** EmailCampaign entity with schedule details

**Pseudocode:**
```
process(campaign):
    validate catFactId exists
    get catFact details
    generate campaign name with current week
    set scheduledDate based on catFact scheduledSendDate
    count total active subscribers
    set totalSubscribers count
    save campaign to database
    return campaign
```

### EmailCampaignExecutionProcessor

**Entity:** EmailCampaign
**Input:** EmailCampaign entity in SCHEDULED state
**Description:** Executes the email campaign
**Output:** EmailCampaign entity with execution results

**Pseudocode:**
```
process(campaign):
    set startedDate to current timestamp
    get catFact for campaign
    get all active subscribers
    
    emailsSent = 0
    emailsFailed = 0
    
    for each subscriber:
        try:
            send email with cat fact
            emailsSent++
            create SubscriberInteraction with type EMAIL_SENT
        catch email sending exception:
            emailsFailed++
            log error
    
    set emailsSent and emailsFailed counts
    update campaign in database
    return campaign
```

### EmailCampaignCompletionProcessor

**Entity:** EmailCampaign
**Input:** EmailCampaign entity in RUNNING state
**Description:** Completes the email campaign
**Output:** EmailCampaign entity marked as completed

**Pseudocode:**
```
process(campaign):
    set completedDate to current timestamp
    update campaign in database
    log campaign completion with statistics
    return campaign
```

### EmailCampaignRetryProcessor

**Entity:** EmailCampaign
**Input:** EmailCampaign entity in FAILED state
**Description:** Retries failed email campaign
**Output:** EmailCampaign entity ready for retry

**Pseudocode:**
```
process(campaign):
    validate campaign is in FAILED state
    reset startedDate and completedDate to null
    reset error message
    update campaign in database
    log retry attempt
    return campaign
```
