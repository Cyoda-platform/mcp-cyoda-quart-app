# Processors

## Subscriber Processors

### 1. SubscriberRegistrationProcessor

**Entity**: Subscriber
**Input Data**: Email, firstName (optional), lastName (optional)
**Description**: Processes new subscriber registration and creates subscriber record.

**Expected Entity Output**: 
- Creates new Subscriber entity with PENDING state
- Generates unique unsubscribe token
- Sets subscription date to current timestamp

**Pseudocode**:
```
process(subscriberData):
    validate email format and uniqueness
    if email already exists and is active:
        throw exception "Email already subscribed"
    
    create new subscriber:
        email = subscriberData.email
        firstName = subscriberData.firstName
        lastName = subscriberData.lastName
        subscriptionDate = current timestamp
        isActive = false
        unsubscribeToken = generate UUID
    
    save subscriber to database
    send welcome email with verification link
    return subscriber
```

### 2. SubscriberActivationProcessor

**Entity**: Subscriber
**Input Data**: Subscriber entity
**Description**: Activates subscriber after email verification.

**Expected Entity Output**: 
- Updates Subscriber entity to ACTIVE state
- Sets isActive to true

**Pseudocode**:
```
process(subscriber):
    validate subscriber exists and is in PENDING state
    
    update subscriber:
        isActive = true
    
    save subscriber to database
    send confirmation email
    log activation event
    return subscriber
```

### 3. SubscriberUnsubscribeProcessor

**Entity**: Subscriber
**Input Data**: Subscriber entity or unsubscribe token
**Description**: Processes unsubscription request.

**Expected Entity Output**: 
- Updates Subscriber entity to UNSUBSCRIBED state
- Sets isActive to false

**Pseudocode**:
```
process(subscriberOrToken):
    if input is token:
        subscriber = find subscriber by unsubscribe token
    else:
        subscriber = input
    
    validate subscriber exists
    
    update subscriber:
        isActive = false
    
    save subscriber to database
    send unsubscribe confirmation email
    log unsubscribe event
    return subscriber
```

---

## CatFact Processors

### 4. CatFactRetrievalProcessor

**Entity**: CatFact
**Input Data**: None (triggered by schedule)
**Description**: Retrieves cat fact from external API and stores it.

**Expected Entity Output**: 
- Creates new CatFact entity with RETRIEVED state

**Pseudocode**:
```
process():
    call external Cat Fact API (https://catfact.ninja/fact)
    if API call fails:
        retry up to 3 times with exponential backoff
        if still fails, throw exception
    
    create new cat fact:
        factText = API response.fact
        factLength = length of factText
        retrievedDate = current timestamp
        externalFactId = API response.id (if available)
    
    save cat fact to database
    log retrieval event
    return cat fact
```

### 5. CatFactSchedulingProcessor

**Entity**: CatFact
**Input Data**: CatFact entity
**Description**: Schedules cat fact for weekly distribution.

**Expected Entity Output**: 
- Updates CatFact entity to SCHEDULED state
- Sets scheduledSendDate

**Pseudocode**:
```
process(catFact):
    validate cat fact exists and is in RETRIEVED state
    
    calculate next send date:
        nextMonday = find next Monday from current date
        scheduledSendDate = nextMonday
    
    update cat fact:
        scheduledSendDate = nextMonday
    
    save cat fact to database
    return cat fact
```

### 6. CatFactDistributionProcessor

**Entity**: CatFact
**Input Data**: CatFact entity
**Description**: Marks cat fact as sent after email distribution.

**Expected Entity Output**: 
- Updates CatFact entity to SENT state

**Pseudocode**:
```
process(catFact):
    validate cat fact exists and is in SCHEDULED state
    
    update cat fact state to SENT
    save cat fact to database
    log distribution completion
    return cat fact
```

### 7. CatFactArchivalProcessor

**Entity**: CatFact
**Input Data**: CatFact entity
**Description**: Archives cat fact after successful distribution.

**Expected Entity Output**:
- Updates CatFact entity to ARCHIVED state

**Pseudocode**:
```
process(catFact):
    validate cat fact exists and is in SENT state

    update cat fact state to ARCHIVED
    save cat fact to database
    log archival event
    return cat fact
```

---

## EmailDelivery Processors

### 8. EmailDeliveryCreationProcessor

**Entity**: EmailDelivery
**Input Data**: Subscriber ID, CatFact ID
**Description**: Creates email delivery record for a subscriber and cat fact.

**Expected Entity Output**:
- Creates new EmailDelivery entity with PENDING state

**Pseudocode**:
```
process(subscriberId, catFactId):
    validate subscriber exists and is active
    validate cat fact exists and is scheduled

    create new email delivery:
        subscriberId = subscriberId
        catFactId = catFactId
        deliveryAttempts = 0
        lastAttemptDate = null
        errorMessage = null

    save email delivery to database
    return email delivery
```

### 9. EmailSendingProcessor

**Entity**: EmailDelivery
**Input Data**: EmailDelivery entity
**Description**: Sends email to subscriber with cat fact content.

**Expected Entity Output**:
- Updates EmailDelivery entity to SENT state
- Updates sentDate and deliveryAttempts

**Pseudocode**:
```
process(emailDelivery):
    validate email delivery exists and is in PENDING state

    subscriber = get subscriber by ID
    catFact = get cat fact by ID

    compose email:
        to = subscriber.email
        subject = "Your Weekly Cat Fact"
        body = create HTML email with cat fact and unsubscribe link

    try:
        send email via email service
        update email delivery:
            sentDate = current timestamp
            deliveryAttempts = deliveryAttempts + 1
            lastAttemptDate = current timestamp

        save email delivery to database
        return email delivery
    catch email sending exception:
        trigger EmailFailureProcessor with error details
```

### 10. EmailFailureProcessor

**Entity**: EmailDelivery
**Input Data**: EmailDelivery entity, error message
**Description**: Handles email sending failure.

**Expected Entity Output**:
- Updates EmailDelivery entity to FAILED state
- Records error message and attempt details

**Pseudocode**:
```
process(emailDelivery, errorMessage):
    validate email delivery exists

    update email delivery:
        errorMessage = errorMessage
        deliveryAttempts = deliveryAttempts + 1
        lastAttemptDate = current timestamp

    save email delivery to database
    log failure event

    if deliveryAttempts < 3:
        schedule retry for later

    return email delivery
```

### 11. EmailRetryProcessor

**Entity**: EmailDelivery
**Input Data**: EmailDelivery entity
**Description**: Retries failed email delivery.

**Expected Entity Output**:
- Updates EmailDelivery entity back to PENDING state for retry

**Pseudocode**:
```
process(emailDelivery):
    validate email delivery exists and is in FAILED state
    validate deliveryAttempts < 3

    reset email delivery for retry:
        errorMessage = null

    save email delivery to database
    return email delivery
```

### 12. EmailDeliveryConfirmationProcessor

**Entity**: EmailDelivery
**Input Data**: EmailDelivery entity
**Description**: Confirms email delivery (tracking).

**Expected Entity Output**:
- Updates EmailDelivery entity to DELIVERED state

**Pseudocode**:
```
process(emailDelivery):
    validate email delivery exists and is in SENT state

    update email delivery state to DELIVERED
    save email delivery to database
    log delivery confirmation
    return email delivery
```

---

## Interaction Processors

### 13. InteractionRecordingProcessor

**Entity**: Interaction
**Input Data**: Subscriber ID, EmailDelivery ID (optional), interaction type, additional data
**Description**: Records user interaction with cat fact emails.

**Expected Entity Output**:
- Creates new Interaction entity with RECORDED state

**Pseudocode**:
```
process(interactionData):
    validate subscriber exists
    if emailDeliveryId provided:
        validate email delivery exists

    create new interaction:
        subscriberId = interactionData.subscriberId
        emailDeliveryId = interactionData.emailDeliveryId
        interactionType = interactionData.type
        interactionDate = current timestamp
        ipAddress = interactionData.ipAddress
        userAgent = interactionData.userAgent
        additionalData = interactionData.additionalData

    save interaction to database
    return interaction
```

### 14. InteractionProcessingProcessor

**Entity**: Interaction
**Input Data**: Interaction entity
**Description**: Processes interaction for analytics and reporting.

**Expected Entity Output**:
- Updates Interaction entity to PROCESSED state
- May trigger other entity transitions (e.g., unsubscribe)

**Pseudocode**:
```
process(interaction):
    validate interaction exists and is in RECORDED state

    if interaction.type == "UNSUBSCRIBE":
        trigger SubscriberUnsubscribeProcessor for subscriber

    update analytics data based on interaction type
    update interaction state to PROCESSED
    save interaction to database
    return interaction
```

---

## WeeklySchedule Processors

### 15. WeeklyScheduleCreationProcessor

**Entity**: WeeklySchedule
**Input Data**: Week start date
**Description**: Creates new weekly schedule for cat fact distribution.

**Expected Entity Output**:
- Creates new WeeklySchedule entity with CREATED state

**Pseudocode**:
```
process(weekStartDate):
    validate weekStartDate is a Monday
    validate no existing schedule for this week

    create new weekly schedule:
        weekStartDate = weekStartDate
        weekEndDate = weekStartDate + 6 days
        scheduledSendDate = weekStartDate (Monday)
        catFactId = null
        totalSubscribers = count active subscribers
        emailsSent = 0
        emailsFailed = 0

    save weekly schedule to database
    return weekly schedule
```

### 16. WeeklyScheduleFactAssignmentProcessor

**Entity**: WeeklySchedule
**Input Data**: WeeklySchedule entity
**Description**: Assigns cat fact to weekly schedule.

**Expected Entity Output**:
- Updates WeeklySchedule entity to FACT_ASSIGNED state
- Sets catFactId

**Pseudocode**:
```
process(weeklySchedule):
    validate weekly schedule exists and is in CREATED state

    availableCatFact = find cat fact in SCHEDULED state for this week
    if no available cat fact:
        trigger CatFactRetrievalProcessor to get new fact
        availableCatFact = newly retrieved fact

    update weekly schedule:
        catFactId = availableCatFact.id

    save weekly schedule to database
    return weekly schedule
```

### 17. WeeklyScheduleEmailDistributionProcessor

**Entity**: WeeklySchedule
**Input Data**: WeeklySchedule entity
**Description**: Distributes emails to all active subscribers.

**Expected Entity Output**:
- Updates WeeklySchedule entity to EMAILS_SENT state
- Creates EmailDelivery entities for all subscribers
- Updates emailsSent and emailsFailed counts

**Pseudocode**:
```
process(weeklySchedule):
    validate weekly schedule exists and is in FACT_ASSIGNED state

    activeSubscribers = get all active subscribers
    catFact = get cat fact by weeklySchedule.catFactId

    emailsSent = 0
    emailsFailed = 0

    for each subscriber in activeSubscribers:
        try:
            create EmailDelivery for subscriber and catFact
            trigger EmailDeliveryCreationProcessor
            emailsSent++
        catch exception:
            emailsFailed++
            log error

    update weekly schedule:
        emailsSent = emailsSent
        emailsFailed = emailsFailed

    trigger CatFactDistributionProcessor for catFact
    save weekly schedule to database
    return weekly schedule
```

### 18. WeeklyScheduleCompletionProcessor

**Entity**: WeeklySchedule
**Input Data**: WeeklySchedule entity
**Description**: Completes weekly cycle and generates reports.

**Expected Entity Output**:
- Updates WeeklySchedule entity to COMPLETED state

**Pseudocode**:
```
process(weeklySchedule):
    validate weekly schedule exists and is in EMAILS_SENT state

    generate weekly report:
        totalSubscribers = weeklySchedule.totalSubscribers
        emailsSent = weeklySchedule.emailsSent
        emailsFailed = weeklySchedule.emailsFailed
        successRate = (emailsSent / totalSubscribers) * 100

    save report to database or send to administrators
    update weekly schedule state to COMPLETED
    save weekly schedule to database

    schedule next week's schedule creation
    return weekly schedule
```
