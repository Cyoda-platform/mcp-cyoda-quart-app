# Criteria

## MailIsHappyCriterion

### Entity
Mail

### Description
Determines if a mail entity should be processed as a happy mail based on the isHappy field.

### Logic
- Check if mail.isHappy equals true
- Return true if the mail is marked as happy
- Return false otherwise

### Pseudocode
```
evaluate(mailEntity):
    return mailEntity.isHappy == true
```

### Usage
Used in the workflow transition from PENDING to HAPPY_SENT state to determine if the mail should be processed by the MailSendHappyMailProcessor.

---

## MailIsGloomyCriterion

### Entity
Mail

### Description
Determines if a mail entity should be processed as a gloomy mail based on the isHappy field.

### Logic
- Check if mail.isHappy equals false
- Return true if the mail is marked as gloomy (not happy)
- Return false otherwise

### Pseudocode
```
evaluate(mailEntity):
    return mailEntity.isHappy == false
```

### Usage
Used in the workflow transition from PENDING to GLOOMY_SENT state to determine if the mail should be processed by the MailSendGloomyMailProcessor.
