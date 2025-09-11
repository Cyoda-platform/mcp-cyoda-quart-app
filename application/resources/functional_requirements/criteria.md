# Criteria

## MailIsHappyCriterion

### Entity
Mail

### Description
Determines if a mail entity should be processed as a happy mail by checking the isHappy field.

### Logic
- Check if mail.isHappy equals true
- Return true if the mail is marked as happy, false otherwise

### Usage
Used in the workflow transition from PENDING to HAPPY_SENT to ensure only happy mails are processed by the MailSendHappyMailProcessor.

### Validation Rules
- isHappy field must be present
- isHappy field must be a boolean value
- Returns true only when isHappy is explicitly true

---

## MailIsGloomyCriterion

### Entity
Mail

### Description
Determines if a mail entity should be processed as a gloomy mail by checking the isHappy field.

### Logic
- Check if mail.isHappy equals false
- Return true if the mail is marked as gloomy (not happy), false otherwise

### Usage
Used in the workflow transition from PENDING to GLOOMY_SENT to ensure only gloomy mails are processed by the MailSendGloomyMailProcessor.

### Validation Rules
- isHappy field must be present
- isHappy field must be a boolean value
- Returns true only when isHappy is explicitly false
