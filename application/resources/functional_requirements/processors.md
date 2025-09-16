# Processors

## Subscriber Processors

### SubscriberRegistrationProcessor

**Entity:** Subscriber
**Input:** Subscriber entity with email, firstName, lastName
**Description:** Processes new subscriber registration
**Output:** Updates subscriber with subscriptionDate, isActive=false, generates unsubscribeToken

**Pseudocode:**
```
process(subscriber):
    validate email format
    check if email already exists
    if email exists and active:
        throw exception "Email already subscribed"
    if email exists and inactive:
        reactivate existing subscriber
        return existing subscriber
    
    set subscriber.subscriptionDate = current timestamp
    set subscriber.isActive = false
    generate unique unsubscribeToken
    set subscriber.unsubscribeToken = token
    save subscriber to database
    
    send welcome email with verification link (optional)
    return updated subscriber
```

### SubscriberActivationProcessor

**Entity:** Subscriber
**Input:** Subscriber entity in pending state
**Description:** Activates subscriber after email verification or auto-activation
**Output:** Updates subscriber with isActive=true

**Pseudocode:**
```
process(subscriber):
    validate subscriber is in pending state
    set subscriber.isActive = true
    save subscriber to database
    
    send confirmation email
    log activation event
    return updated subscriber
```

### SubscriberUnsubscribeProcessor

**Entity:** Subscriber
**Input:** Subscriber entity with unsubscribe request
**Description:** Processes subscriber unsubscription
**Output:** Updates subscriber with isActive=false

**Pseudocode:**
```
process(subscriber):
    validate subscriber exists and is active
    set subscriber.isActive = false
    save subscriber to database
    
    send unsubscribe confirmation email
    log unsubscribe event
    return updated subscriber
```

### SubscriberBounceProcessor

**Entity:** Subscriber
**Input:** Subscriber entity with bounce information
**Description:** Handles permanent email bounces
**Output:** Updates subscriber with isActive=false

**Pseudocode:**
```
process(subscriber):
    validate subscriber exists
    set subscriber.isActive = false
    save subscriber to database
    
    log bounce event with reason
    return updated subscriber
```

### SubscriberReactivationProcessor

**Entity:** Subscriber
**Input:** Subscriber entity for reactivation
**Description:** Manually reactivates bounced subscriber
**Output:** Updates subscriber with isActive=true

**Pseudocode:**
```
process(subscriber):
    validate subscriber exists and is in bounced state
    set subscriber.isActive = true
    save subscriber to database
    
    send reactivation confirmation email
    log reactivation event
    return updated subscriber
```

---

## CatFact Processors

### CatFactRetrievalProcessor

**Entity:** CatFact
**Input:** Empty CatFact entity
**Description:** Retrieves cat fact from external API
**Output:** Updates CatFact with fact data

**Pseudocode:**
```
process(catFact):
    call Cat Fact API (https://catfact.ninja/fact)
    if API call successful:
        set catFact.fact = response.fact
        set catFact.length = response.length or fact.length
        set catFact.apiFactId = response.id (if available)
        set catFact.retrievedDate = current timestamp
        save catFact to database
    else:
        throw exception "Failed to retrieve cat fact from API"
    
    return updated catFact
```

### CatFactSchedulingProcessor

**Entity:** CatFact
**Input:** CatFact entity with retrieved fact
**Description:** Schedules cat fact for weekly distribution
**Output:** Updates CatFact with scheduledSendDate

**Pseudocode:**
```
process(catFact):
    validate catFact has fact content
    calculate next weekly send date (e.g., every Monday at 9 AM)
    set catFact.scheduledSendDate = calculated date
    save catFact to database
    
    return updated catFact
```

### CatFactDistributionProcessor

**Entity:** CatFact
**Input:** CatFact entity ready for distribution
**Description:** Distributes cat fact to all active subscribers
**Output:** Creates EmailDelivery entities for each subscriber

**Pseudocode:**
```
process(catFact):
    validate catFact is scheduled and ready to send
    get all active subscribers from database
    
    for each active subscriber:
        create new EmailDelivery entity
        set emailDelivery.subscriberId = subscriber.id
        set emailDelivery.catFactId = catFact.id
        set emailDelivery.deliveryAttempts = 0
        trigger EmailDelivery workflow with transition to pending
    
    return catFact (no changes to catFact entity)
```

### CatFactArchiveProcessor

**Entity:** CatFact
**Input:** CatFact entity that has been sent
**Description:** Archives cat fact after distribution
**Output:** Updates CatFact (no specific changes, just state transition)

**Pseudocode:**
```
process(catFact):
    validate catFact has been sent
    log archival event
    
    return catFact (no entity changes, just state transition)
```

---

## EmailDelivery Processors

### EmailDeliveryQueueProcessor

**Entity:** EmailDelivery
**Input:** EmailDelivery entity for queuing
**Description:** Queues email for delivery
**Output:** Updates EmailDelivery with queue timestamp

**Pseudocode:**
```
process(emailDelivery):
    validate emailDelivery has subscriberId and catFactId
    get subscriber and catFact details
    validate subscriber is active
    
    set emailDelivery.deliveryAttempts = 0
    set emailDelivery.lastAttemptDate = current timestamp
    save emailDelivery to database
    
    return updated emailDelivery
```

### EmailDeliverySendProcessor

**Entity:** EmailDelivery
**Input:** EmailDelivery entity ready for sending
**Description:** Sends email to subscriber
**Output:** Updates EmailDelivery with sent status

**Pseudocode:**
```
process(emailDelivery):
    get subscriber details
    get catFact details
    
    compose email with:
        - subject: "Your Weekly Cat Fact"
        - body: catFact.fact
        - unsubscribe link with subscriber.unsubscribeToken
        - tracking pixel for open tracking
    
    send email via email service
    if send successful:
        set emailDelivery.sentDate = current timestamp
        increment emailDelivery.deliveryAttempts
        set emailDelivery.lastAttemptDate = current timestamp
        save emailDelivery to database
    else:
        throw exception "Email send failed"
    
    return updated emailDelivery
```

### EmailDeliveryConfirmationProcessor

**Entity:** EmailDelivery
**Input:** EmailDelivery entity with delivery confirmation
**Description:** Confirms email delivery
**Output:** Updates EmailDelivery (no specific changes, just state transition)

**Pseudocode:**
```
process(emailDelivery):
    validate emailDelivery was sent
    log delivery confirmation
    
    return emailDelivery (no entity changes, just state transition)
```

### EmailDeliveryOpenProcessor

**Entity:** EmailDelivery
**Input:** EmailDelivery entity with open tracking data
**Description:** Tracks email opening
**Output:** Updates EmailDelivery with open status

**Pseudocode:**
```
process(emailDelivery):
    validate emailDelivery was delivered
    set emailDelivery.opened = true
    set emailDelivery.openedDate = current timestamp
    save emailDelivery to database
    
    log email open event
    return updated emailDelivery
```

### EmailDeliveryFailureProcessor

**Entity:** EmailDelivery
**Input:** EmailDelivery entity with failure information
**Description:** Handles email delivery failure
**Output:** Updates EmailDelivery with error details

**Pseudocode:**
```
process(emailDelivery):
    increment emailDelivery.deliveryAttempts
    set emailDelivery.lastAttemptDate = current timestamp
    set emailDelivery.errorMessage = failure reason
    save emailDelivery to database
    
    if deliveryAttempts >= max retry limit:
        trigger Subscriber workflow with bounce transition
    
    return updated emailDelivery
```

### EmailDeliveryRetryProcessor

**Entity:** EmailDelivery
**Input:** EmailDelivery entity for retry
**Description:** Retries failed email delivery
**Output:** Resets EmailDelivery for retry

**Pseudocode:**
```
process(emailDelivery):
    validate emailDelivery is in failed state
    validate retry attempts are within limit
    
    clear emailDelivery.errorMessage
    set emailDelivery.lastAttemptDate = current timestamp
    save emailDelivery to database
    
    return updated emailDelivery
```

### EmailDeliveryBounceProcessor

**Entity:** EmailDelivery
**Input:** EmailDelivery entity with bounce information
**Description:** Handles permanent email bounce
**Output:** Updates EmailDelivery with bounce details

**Pseudocode:**
```
process(emailDelivery):
    set emailDelivery.errorMessage = bounce reason
    save emailDelivery to database
    
    trigger Subscriber workflow with bounce transition
    log bounce event
    
    return updated emailDelivery
```

---

## WeeklySchedule Processors

### WeeklyScheduleCreationProcessor

**Entity:** WeeklySchedule
**Input:** WeeklySchedule entity for creation
**Description:** Creates weekly schedule for cat fact distribution
**Output:** Updates WeeklySchedule with schedule details

**Pseudocode:**
```
process(weeklySchedule):
    calculate current week start and end dates
    set weeklySchedule.weekStartDate = week start
    set weeklySchedule.weekEndDate = week end
    set weeklySchedule.scheduledDate = next Monday 9 AM
    count active subscribers
    set weeklySchedule.subscriberCount = active count
    save weeklySchedule to database
    
    return updated weeklySchedule
```

### WeeklyScheduleFactRetrievalProcessor

**Entity:** WeeklySchedule
**Input:** WeeklySchedule entity ready for fact retrieval
**Description:** Retrieves cat fact for weekly distribution
**Output:** Updates WeeklySchedule with catFactId

**Pseudocode:**
```
process(weeklySchedule):
    create new CatFact entity
    trigger CatFact workflow with retrieval transition
    wait for CatFact to be retrieved and scheduled
    
    set weeklySchedule.catFactId = catFact.id
    save weeklySchedule to database
    
    return updated weeklySchedule
```

### WeeklyScheduleEmailDistributionProcessor

**Entity:** WeeklySchedule
**Input:** WeeklySchedule entity with retrieved cat fact
**Description:** Initiates email distribution to all subscribers
**Output:** Updates WeeklySchedule (no specific changes)

**Pseudocode:**
```
process(weeklySchedule):
    get catFact by weeklySchedule.catFactId
    trigger CatFact workflow with distribution transition
    
    return weeklySchedule (no entity changes)
```

### WeeklyScheduleCompletionProcessor

**Entity:** WeeklySchedule
**Input:** WeeklySchedule entity after email distribution
**Description:** Completes weekly schedule
**Output:** Updates WeeklySchedule with execution timestamp

**Pseudocode:**
```
process(weeklySchedule):
    set weeklySchedule.executedDate = current timestamp
    save weeklySchedule to database
    
    log completion event
    schedule next week's WeeklySchedule creation
    
    return updated weeklySchedule
```
