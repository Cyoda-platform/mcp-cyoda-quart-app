# Criteria

## CatFact Criteria

### 1. CatFactSchedulingCriterion

**Entity**: CatFact
**Description**: Checks if a cat fact can be scheduled for weekly distribution.

**Validation Logic**:
- Cat fact must be in RETRIEVED state
- Cat fact text must not be empty
- Cat fact text length must be between 10 and 500 characters
- No other cat fact should be scheduled for the same week

**Pseudocode**:
```
evaluate(catFact):
    if catFact.state != RETRIEVED:
        return false, "Cat fact must be in RETRIEVED state"
    
    if catFact.factText is null or empty:
        return false, "Cat fact text cannot be empty"
    
    if catFact.factLength < 10 or catFact.factLength > 500:
        return false, "Cat fact text must be between 10 and 500 characters"
    
    nextMonday = find next Monday from current date
    existingScheduledFact = find cat fact with scheduledSendDate = nextMonday
    if existingScheduledFact exists:
        return false, "Another cat fact is already scheduled for this week"
    
    return true, "Cat fact can be scheduled"
```

### 2. CatFactArchivalCriterion

**Entity**: CatFact
**Description**: Checks if a cat fact can be archived after distribution.

**Validation Logic**:
- Cat fact must be in SENT state
- All related email deliveries must be completed (SENT, FAILED, or DELIVERED)
- At least 24 hours must have passed since the cat fact was sent

**Pseudocode**:
```
evaluate(catFact):
    if catFact.state != SENT:
        return false, "Cat fact must be in SENT state"
    
    emailDeliveries = find all email deliveries for catFact
    for each delivery in emailDeliveries:
        if delivery.state == PENDING:
            return false, "Some email deliveries are still pending"
    
    if catFact.scheduledSendDate is null:
        return false, "Cat fact has no scheduled send date"
    
    hoursSinceSent = hours between catFact.scheduledSendDate and current time
    if hoursSinceSent < 24:
        return false, "Must wait at least 24 hours before archiving"
    
    return true, "Cat fact can be archived"
```

---

## EmailDelivery Criteria

### 3. EmailRetryCriterion

**Entity**: EmailDelivery
**Description**: Checks if a failed email delivery can be retried.

**Validation Logic**:
- Email delivery must be in FAILED state
- Number of delivery attempts must be less than 3
- At least 30 minutes must have passed since the last attempt
- Subscriber must still be active

**Pseudocode**:
```
evaluate(emailDelivery):
    if emailDelivery.state != FAILED:
        return false, "Email delivery must be in FAILED state"
    
    if emailDelivery.deliveryAttempts >= 3:
        return false, "Maximum retry attempts (3) exceeded"
    
    if emailDelivery.lastAttemptDate is null:
        return false, "No previous attempt date found"
    
    minutesSinceLastAttempt = minutes between emailDelivery.lastAttemptDate and current time
    if minutesSinceLastAttempt < 30:
        return false, "Must wait at least 30 minutes before retry"
    
    subscriber = find subscriber by emailDelivery.subscriberId
    if subscriber is null or not subscriber.isActive:
        return false, "Subscriber is no longer active"
    
    return true, "Email delivery can be retried"
```

---

## WeeklySchedule Criteria

### 4. WeeklyScheduleFactAvailabilityCriterion

**Entity**: WeeklySchedule
**Description**: Checks if a cat fact is available for assignment to weekly schedule.

**Validation Logic**:
- Weekly schedule must be in CREATED state
- There must be at least one cat fact in SCHEDULED state for the current week
- If no scheduled cat fact exists, system should be able to retrieve a new one

**Pseudocode**:
```
evaluate(weeklySchedule):
    if weeklySchedule.state != CREATED:
        return false, "Weekly schedule must be in CREATED state"
    
    scheduledCatFacts = find cat facts with scheduledSendDate = weeklySchedule.scheduledSendDate
    if scheduledCatFacts.size() > 0:
        return true, "Scheduled cat fact available for assignment"
    
    // Check if we can retrieve a new cat fact
    try:
        testApiCall = call Cat Fact API with timeout
        if testApiCall is successful:
            return true, "Can retrieve new cat fact from API"
        else:
            return false, "Cat Fact API is not available"
    catch exception:
        return false, "Cannot retrieve cat fact: " + exception.message
```

---

## Subscriber Criteria

### 5. SubscriberValidationCriterion

**Entity**: Subscriber
**Description**: Validates subscriber data during registration and updates.

**Validation Logic**:
- Email must be valid format
- Email must be unique (for new registrations)
- First name and last name must not contain special characters (if provided)

**Pseudocode**:
```
evaluate(subscriber):
    if subscriber.email is null or empty:
        return false, "Email is required"
    
    if not isValidEmailFormat(subscriber.email):
        return false, "Invalid email format"
    
    // For new registrations, check uniqueness
    if subscriber.id is null:
        existingSubscriber = find subscriber by email
        if existingSubscriber exists and existingSubscriber.isActive:
            return false, "Email is already subscribed"
    
    if subscriber.firstName is not null:
        if containsSpecialCharacters(subscriber.firstName):
            return false, "First name cannot contain special characters"
    
    if subscriber.lastName is not null:
        if containsSpecialCharacters(subscriber.lastName):
            return false, "Last name cannot contain special characters"
    
    return true, "Subscriber data is valid"
```

---

## Interaction Criteria

### 6. InteractionValidationCriterion

**Entity**: Interaction
**Description**: Validates interaction data before recording.

**Validation Logic**:
- Subscriber must exist and be active
- Interaction type must be valid
- Email delivery must exist (if provided)

**Pseudocode**:
```
evaluate(interaction):
    subscriber = find subscriber by interaction.subscriberId
    if subscriber is null:
        return false, "Subscriber not found"
    
    if not subscriber.isActive and interaction.interactionType != "UNSUBSCRIBE":
        return false, "Subscriber is not active"
    
    validInteractionTypes = ["EMAIL_OPEN", "LINK_CLICK", "UNSUBSCRIBE", "BOUNCE", "COMPLAINT"]
    if interaction.interactionType not in validInteractionTypes:
        return false, "Invalid interaction type"
    
    if interaction.emailDeliveryId is not null:
        emailDelivery = find email delivery by interaction.emailDeliveryId
        if emailDelivery is null:
            return false, "Email delivery not found"
        
        if emailDelivery.subscriberId != interaction.subscriberId:
            return false, "Email delivery does not belong to this subscriber"
    
    return true, "Interaction data is valid"
```
