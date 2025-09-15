# Criteria

## 1. CatFact Criteria

### CatFactReadyCriterion

**Entity:** CatFact
**Description:** Checks if a cat fact is ready to be sent (scheduled date has arrived and it's the correct time).

**Validation Logic:**
- Current date equals or is after the scheduled send date
- Current time is within the configured sending window (e.g., between 9 AM and 11 AM)
- Cat fact has valid content (not empty or null)

**Pseudocode:**
```
evaluate(catFactEntity):
    1. Get current date and time
    2. Check if current date >= catFact.scheduledSendDate
    3. Check if current time is within sending window (9 AM - 11 AM)
    4. Check if catFact.factText is not null and not empty
    5. Return true if all conditions are met, false otherwise
```

### CatFactFailureCriterion

**Entity:** CatFact
**Description:** Checks if a cat fact sending has failed based on various failure conditions.

**Validation Logic:**
- Maximum retry attempts exceeded
- Critical error occurred during sending
- All subscribers failed to receive the email
- External service unavailable for extended period

**Pseudocode:**
```
evaluate(catFactEntity):
    1. Check if retry count exceeds maximum allowed retries (3)
    2. Check if critical system error flag is set
    3. Check if all email sending attempts failed
    4. Check if external email service is unavailable for > 2 hours
    5. Return true if any failure condition is met, false otherwise
```

---

## 2. EmailCampaign Criteria

### EmailCampaignReadyCriterion

**Entity:** EmailCampaign
**Description:** Checks if an email campaign is ready to be executed.

**Validation Logic:**
- Campaign is scheduled for current date
- Associated cat fact is available and valid
- At least one active subscriber exists
- Email service is operational

**Pseudocode:**
```
evaluate(emailCampaignEntity):
    1. Get current date
    2. Check if campaign.campaignDate <= current date
    3. Get associated cat fact by campaign.catFactId
    4. Check if cat fact exists and has valid content
    5. Check if there are active subscribers (campaign.totalSubscribers > 0)
    6. Check if email service is operational (health check)
    7. Return true if all conditions are met, false otherwise
```

### EmailCampaignSuccessCriterion

**Entity:** EmailCampaign
**Description:** Checks if an email campaign has completed successfully.

**Validation Logic:**
- All emails have been processed (sent or failed)
- Success rate is above minimum threshold (e.g., 80%)
- No critical errors occurred during execution

**Pseudocode:**
```
evaluate(emailCampaignEntity):
    1. Calculate total emails processed = campaign.emailsSent + campaign.emailsFailed
    2. Check if total processed >= campaign.totalSubscribers
    3. Calculate success rate = campaign.emailsSent / campaign.totalSubscribers
    4. Check if success rate >= minimum threshold (0.8)
    5. Check if no critical errors occurred during execution
    6. Return true if all conditions are met, false otherwise
```

### EmailCampaignFailureCriterion

**Entity:** EmailCampaign
**Description:** Checks if an email campaign has failed and should be marked as failed.

**Validation Logic:**
- Success rate is below minimum threshold
- Critical system error occurred
- Email service is unavailable
- Execution timeout exceeded

**Pseudocode:**
```
evaluate(emailCampaignEntity):
    1. Calculate success rate = campaign.emailsSent / campaign.totalSubscribers
    2. Check if success rate < minimum threshold (0.5)
    3. Check if critical system error flag is set
    4. Check if email service is unavailable
    5. Check if execution time exceeds maximum allowed time (2 hours)
    6. Return true if any failure condition is met, false otherwise
```

---

## 3. Subscriber Criteria

### SubscriberValidEmailCriterion

**Entity:** Subscriber
**Description:** Validates that a subscriber has a valid email address format.

**Validation Logic:**
- Email format is valid (contains @ and valid domain)
- Email is not in blacklist
- Email domain is not blocked

**Pseudocode:**
```
evaluate(subscriberEntity):
    1. Check if subscriber.email matches valid email regex pattern
    2. Check if subscriber.email is not in blacklisted emails list
    3. Check if email domain is not in blocked domains list
    4. Return true if all validations pass, false otherwise
```

### SubscriberConfirmationTokenValidCriterion

**Entity:** Subscriber
**Description:** Validates that a confirmation token is valid and not expired.

**Validation Logic:**
- Token matches the stored confirmation token
- Token is not expired (within 24 hours of creation)
- Subscriber is in PENDING_CONFIRMATION state

**Pseudocode:**
```
evaluate(subscriberEntity, inputToken):
    1. Check if inputToken equals subscriber.confirmationToken
    2. Check if subscriber.subscriptionDate is within last 24 hours
    3. Check if subscriber state is PENDING_CONFIRMATION
    4. Return true if all conditions are met, false otherwise
```

### SubscriberUnsubscribeTokenValidCriterion

**Entity:** Subscriber
**Description:** Validates that an unsubscribe token is valid.

**Validation Logic:**
- Token matches the stored unsubscribe token
- Subscriber is in ACTIVE or PENDING_CONFIRMATION state

**Pseudocode:**
```
evaluate(subscriberEntity, inputToken):
    1. Check if inputToken equals subscriber.unsubscribeToken
    2. Check if subscriber state is ACTIVE or PENDING_CONFIRMATION
    3. Return true if all conditions are met, false otherwise
```

---

## 4. SubscriberInteraction Criteria

### SubscriberInteractionValidCriterion

**Entity:** SubscriberInteraction
**Description:** Validates that a subscriber interaction is valid and can be recorded.

**Validation Logic:**
- Subscriber exists and is valid
- Cat fact exists (if applicable)
- Interaction type is valid
- No duplicate interaction within short time window

**Pseudocode:**
```
evaluate(subscriberInteractionEntity):
    1. Check if subscriber with subscriberId exists
    2. If catFactId is provided, check if cat fact exists
    3. Check if interactionType is in valid types list
    4. Check if no duplicate interaction exists within last 5 minutes
    5. Return true if all validations pass, false otherwise
```

---

## 5. System Criteria

### EmailServiceHealthCriterion

**Description:** Checks if the email service is healthy and operational.

**Validation Logic:**
- Email service responds to health check
- Email service has not exceeded rate limits
- Email service authentication is valid

**Pseudocode:**
```
evaluate():
    1. Perform health check call to email service
    2. Check if response is successful (HTTP 200)
    3. Check if rate limit headers indicate available capacity
    4. Check if authentication credentials are valid
    5. Return true if all checks pass, false otherwise
```

### WeeklyScheduleCriterion

**Description:** Checks if it's the correct time for weekly cat fact distribution.

**Validation Logic:**
- Current day is Monday
- Current time is within configured sending window
- No cat fact has been sent this week already

**Pseudocode:**
```
evaluate():
    1. Check if current day of week is Monday
    2. Check if current time is between 9 AM and 11 AM
    3. Check if no cat fact with state SENT exists for current week
    4. Return true if all conditions are met, false otherwise
```
