# Processors

## MailSendHappyMailProcessor

### Entity
Mail

### Description
Processes and sends happy mail messages to the recipients in the mail list.

### Expected Input Data
- Mail entity with:
  - isHappy: true
  - mailList: array of valid email addresses

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
       - Log successful delivery
    5. Update mail entity delivery status
    6. Return success status
```

### Expected Output
- Mail entity state transitions to HAPPY_SENT
- No other entity updates required
- Transition name: null (state managed by workflow)

### Error Handling
- If any email fails to send, log error but continue with remaining emails
- If all emails fail, throw exception to trigger FAILED state

---

## MailSendGloomyMailProcessor

### Entity
Mail

### Description
Processes and sends gloomy mail messages to the recipients in the mail list.

### Expected Input Data
- Mail entity with:
  - isHappy: false
  - mailList: array of valid email addresses

### Process Logic (Pseudocode)
```
process(mailEntity):
    1. Validate mailList is not empty
    2. Validate all email addresses in mailList are valid format
    3. Generate gloomy mail content:
       - Subject: "☔ Gloomy Mail - Sharing the Blues"
       - Body: Create melancholic, somber message content
    4. For each email in mailList:
       - Send email with gloomy content
       - Log successful delivery
    5. Update mail entity delivery status
    6. Return success status
```

### Expected Output
- Mail entity state transitions to GLOOMY_SENT
- No other entity updates required
- Transition name: null (state managed by workflow)

### Error Handling
- If any email fails to send, log error but continue with remaining emails
- If all emails fail, throw exception to trigger FAILED state
