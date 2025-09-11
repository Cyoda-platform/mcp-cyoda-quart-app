# Processors

## MailSendHappyMailProcessor

### Description
Processes and sends happy mail to the recipients in the mail list.

### Entity
Mail

### Expected Input Data
- Mail entity with:
  - isHappy: true
  - mailList: array of valid email addresses
  - entity.meta.state: "pending"

### Process Logic (Pseudocode)
```
process(mailEntity):
    1. Validate that mailEntity.isHappy is true
    2. Validate that mailEntity.mailList is not empty
    3. Generate happy mail content:
       - Subject: "🌟 Happy Mail - Brighten Your Day! 🌟"
       - Body: Create cheerful message with positive content, emojis, and uplifting quotes
    4. For each email in mailEntity.mailList:
       - Send email with happy content
       - Log successful delivery
    5. Update mail entity state to "happy_sent"
    6. Return updated mail entity
```

### Expected Output
- Modified Mail entity with state changed to "happy_sent"
- No other entities are created or modified
- Transition: pending → happy_sent

### Error Handling
- If email sending fails, log error and throw exception
- If mailList is empty, throw validation exception
- If isHappy is false, throw validation exception

---

## MailSendGloomyMailProcessor

### Description
Processes and sends gloomy mail to the recipients in the mail list.

### Entity
Mail

### Expected Input Data
- Mail entity with:
  - isHappy: false
  - mailList: array of valid email addresses
  - entity.meta.state: "pending"

### Process Logic (Pseudocode)
```
process(mailEntity):
    1. Validate that mailEntity.isHappy is false
    2. Validate that mailEntity.mailList is not empty
    3. Generate gloomy mail content:
       - Subject: "☔ Reflective Mail - A Moment of Contemplation ☔"
       - Body: Create thoughtful message with introspective content and gentle support
    4. For each email in mailEntity.mailList:
       - Send email with gloomy content
       - Log successful delivery
    5. Update mail entity state to "gloomy_sent"
    6. Return updated mail entity
```

### Expected Output
- Modified Mail entity with state changed to "gloomy_sent"
- No other entities are created or modified
- Transition: pending → gloomy_sent

### Error Handling
- If email sending fails, log error and throw exception
- If mailList is empty, throw validation exception
- If isHappy is true, throw validation exception

### Notes
- Both processors handle email delivery through the configured email service
- Email content is generated based on the happiness state of the mail
- Processors validate input data before processing
- All email deliveries are logged for audit purposes
