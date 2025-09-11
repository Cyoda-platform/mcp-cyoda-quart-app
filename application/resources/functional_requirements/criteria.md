# Criteria

## MailIsHappyCriterion

### Description
Determines if a mail entity should be processed as a happy mail.

### Entity
Mail

### Logic
Checks if the `isHappy` field of the mail entity is set to `true`.

### Implementation
```
evaluate(mailEntity):
    return mailEntity.isHappy == true
```

### Usage
- Used in the workflow transition from "pending" to "happy_sent"
- Ensures that only mails marked as happy are processed by the MailSendHappyMailProcessor

### Return Value
- **true**: If the mail is happy (isHappy = true)
- **false**: If the mail is not happy (isHappy = false)

---

## MailIsGloomyCriterion

### Description
Determines if a mail entity should be processed as a gloomy mail.

### Entity
Mail

### Logic
Checks if the `isHappy` field of the mail entity is set to `false`.

### Implementation
```
evaluate(mailEntity):
    return mailEntity.isHappy == false
```

### Usage
- Used in the workflow transition from "pending" to "gloomy_sent"
- Ensures that only mails marked as gloomy are processed by the MailSendGloomyMailProcessor

### Return Value
- **true**: If the mail is gloomy (isHappy = false)
- **false**: If the mail is not gloomy (isHappy = true)

### Notes
- These criteria are mutually exclusive - a mail cannot be both happy and gloomy
- The criteria provide clear decision points in the workflow
- Simple boolean evaluation ensures reliable workflow routing
- Both criteria validate the same field but with opposite conditions
