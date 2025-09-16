# Criteria

## Subscriber Criteria

### SubscriberBounceCriterion

**Entity:** Subscriber
**Description:** Checks if subscriber should be marked as bounced based on email delivery failures
**Condition:** Multiple permanent bounce failures or hard bounce received

**Logic:**
```
evaluate(subscriber):
    get recent EmailDelivery records for subscriber
    count permanent bounce failures in last 30 days
    
    if permanent_bounce_count >= 3:
        return true
    
    get latest EmailDelivery for subscriber
    if latest delivery has hard bounce error:
        return true
    
    return false
```

---

## CatFact Criteria

### CatFactSendTimeCriterion

**Entity:** CatFact
**Description:** Checks if it's time to send the scheduled cat fact
**Condition:** Current time is at or after the scheduled send time

**Logic:**
```
evaluate(catFact):
    if catFact.scheduledSendDate is null:
        return false
    
    current_time = get current timestamp
    
    if current_time >= catFact.scheduledSendDate:
        return true
    
    return false
```

---

## EmailDelivery Criteria

### EmailDeliverySuccessCriterion

**Entity:** EmailDelivery
**Description:** Checks if email delivery was successful
**Condition:** Email service confirms successful delivery

**Logic:**
```
evaluate(emailDelivery):
    if emailDelivery.sentDate is null:
        return false
    
    if emailDelivery.errorMessage is not null:
        return false
    
    check delivery status with email service provider
    if delivery_status == "delivered":
        return true
    
    return false
```

### EmailDeliveryOpenCriterion

**Entity:** EmailDelivery
**Description:** Checks if email was opened by recipient
**Condition:** Tracking pixel was loaded or open event received

**Logic:**
```
evaluate(emailDelivery):
    if emailDelivery.opened == true:
        return true
    
    check tracking data for email open events
    if open_event_detected:
        return true
    
    return false
```

### EmailDeliveryFailureCriterion

**Entity:** EmailDelivery
**Description:** Checks if email delivery failed
**Condition:** Email service reports delivery failure

**Logic:**
```
evaluate(emailDelivery):
    if emailDelivery.errorMessage is not null:
        return true
    
    check delivery status with email service provider
    if delivery_status in ["failed", "rejected", "bounced"]:
        return true
    
    if emailDelivery.deliveryAttempts > 0 and emailDelivery.sentDate is null:
        return true
    
    return false
```

### EmailDeliveryRetryCriterion

**Entity:** EmailDelivery
**Description:** Checks if failed email delivery can be retried
**Condition:** Delivery attempts are below retry limit and failure is not permanent

**Logic:**
```
evaluate(emailDelivery):
    max_retry_attempts = 3
    
    if emailDelivery.deliveryAttempts >= max_retry_attempts:
        return false
    
    if emailDelivery.errorMessage contains "permanent" or "hard bounce":
        return false
    
    if emailDelivery.errorMessage contains "invalid email":
        return false
    
    time_since_last_attempt = current_time - emailDelivery.lastAttemptDate
    min_retry_interval = 1 hour
    
    if time_since_last_attempt >= min_retry_interval:
        return true
    
    return false
```

### EmailDeliveryBounceCriterion

**Entity:** EmailDelivery
**Description:** Checks if email delivery resulted in a permanent bounce
**Condition:** Email service reports hard bounce or permanent failure

**Logic:**
```
evaluate(emailDelivery):
    if emailDelivery.errorMessage is null:
        return false
    
    hard_bounce_indicators = [
        "hard bounce",
        "permanent failure",
        "invalid email",
        "mailbox does not exist",
        "domain not found",
        "recipient rejected"
    ]
    
    error_message_lower = emailDelivery.errorMessage.toLowerCase()
    
    for indicator in hard_bounce_indicators:
        if indicator in error_message_lower:
            return true
    
    check bounce classification with email service provider
    if bounce_type == "hard" or bounce_type == "permanent":
        return true
    
    return false
```

---

## WeeklySchedule Criteria

### WeeklyScheduleTimeCriterion

**Entity:** WeeklySchedule
**Description:** Checks if it's time to retrieve cat fact for weekly distribution
**Condition:** Current time is at or after the scheduled time

**Logic:**
```
evaluate(weeklySchedule):
    if weeklySchedule.scheduledDate is null:
        return false
    
    current_time = get current timestamp
    
    if current_time >= weeklySchedule.scheduledDate:
        return true
    
    return false
```

---

## General Validation Criteria

### EmailValidationCriterion

**Entity:** Subscriber
**Description:** Validates email format and domain
**Condition:** Email has valid format and domain exists

**Logic:**
```
evaluate(subscriber):
    email = subscriber.email
    
    if email is null or empty:
        return false
    
    if not matches_email_regex(email):
        return false
    
    domain = extract_domain(email)
    if not domain_exists(domain):
        return false
    
    if domain in blocked_domains_list:
        return false
    
    return true
```

### ActiveSubscriberCriterion

**Entity:** Subscriber
**Description:** Checks if subscriber is active and can receive emails
**Condition:** Subscriber is active and not bounced

**Logic:**
```
evaluate(subscriber):
    if subscriber.isActive != true:
        return false
    
    if subscriber.meta.state == "bounced":
        return false
    
    if subscriber.meta.state == "unsubscribed":
        return false
    
    return true
```
