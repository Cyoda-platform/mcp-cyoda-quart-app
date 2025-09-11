# Processors

## MailSendHappyMailProcessor

### Entity
Mail

### Description
Processes the sending of happy mail messages to the recipients in the mail list.

### Input Data
- Mail entity with isHappy = true
- mailList containing recipient email addresses

### Process Logic (Pseudocode)
```
process(mailEntity):
    1. Validate mailList is not empty
    2. Validate all email addresses in mailList are valid format
    3. Generate happy mail content:
       - Subject: "🌟 Happy Mail - Brighten Your Day!"
       - Body: Create cheerful, positive message content
    4. For each email in mailList:
       - Send email with happy content
       - Log successful sends
       - Handle any send failures
    5. Update mail entity with send results
    6. Return updated mail entity
```

### Expected Output
- Mail entity with updated metadata about send status
- Entity state will transition to HAPPY_SENT automatically
- No other entity updates required

### Transition
- Target transition: PENDING → HAPPY_SENT

---

## MailSendGloomyMailProcessor

### Entity
Mail

### Description
Processes the sending of gloomy mail messages to the recipients in the mail list.

### Input Data
- Mail entity with isHappy = false
- mailList containing recipient email addresses

### Process Logic (Pseudocode)
```
process(mailEntity):
    1. Validate mailList is not empty
    2. Validate all email addresses in mailList are valid format
    3. Generate gloomy mail content:
       - Subject: "☔ Gloomy Mail - Reflective Thoughts"
       - Body: Create thoughtful, melancholic message content
    4. For each email in mailList:
       - Send email with gloomy content
       - Log successful sends
       - Handle any send failures
    5. Update mail entity with send results
    6. Return updated mail entity
```

### Expected Output
- Mail entity with updated metadata about send status
- Entity state will transition to GLOOMY_SENT automatically
- No other entity updates required

### Transition
- Target transition: PENDING → GLOOMY_SENT
