# Processors

## MailSendHappyMailProcessor

### Entity
Mail

### Description
Processes and sends happy mail messages to the specified recipients. This processor handles the delivery of positive/uplifting email content.

### Expected Input Data
- Mail entity in HAPPY state
- Mail entity must have:
  - mailList: Valid comma-separated email addresses
  - content: Email body content
  - subject: Email subject line

### Process Logic (Pseudocode)
```
process(mailEntity):
    1. Validate mail entity is in HAPPY state
    2. Parse mailList to extract individual email addresses
    3. Validate all email addresses are properly formatted
    4. Prepare happy mail template with:
       - Add positive greeting/header
       - Include original content
       - Add uplifting footer/signature
    5. For each email address in mailList:
       - Send email with prepared content
       - Log successful delivery
    6. Update mailEntity.sentAt with current timestamp
    7. Return updated mailEntity
    
    If any step fails:
       - Log error details
       - Throw exception to trigger FAILED state transition
```

### Expected Output
- Updated Mail entity with sentAt timestamp
- Transition to SENT state (automatic)
- If failure occurs: Transition to FAILED state

### Other Entity Updates
None

---

## MailSendGloomyMailProcessor

### Entity
Mail

### Description
Processes and sends gloomy mail messages to the specified recipients. This processor handles the delivery of sad/melancholic email content with appropriate sensitivity.

### Expected Input Data
- Mail entity in GLOOMY state
- Mail entity must have:
  - mailList: Valid comma-separated email addresses
  - content: Email body content
  - subject: Email subject line

### Process Logic (Pseudocode)
```
process(mailEntity):
    1. Validate mail entity is in GLOOMY state
    2. Parse mailList to extract individual email addresses
    3. Validate all email addresses are properly formatted
    4. Prepare gloomy mail template with:
       - Add gentle/empathetic greeting
       - Include original content
       - Add supportive footer with resources/help
    5. For each email address in mailList:
       - Send email with prepared content
       - Log successful delivery
    6. Update mailEntity.sentAt with current timestamp
    7. Return updated mailEntity
    
    If any step fails:
       - Log error details
       - Throw exception to trigger FAILED state transition
```

### Expected Output
- Updated Mail entity with sentAt timestamp
- Transition to SENT state (automatic)
- If failure occurs: Transition to FAILED state

### Other Entity Updates
None
