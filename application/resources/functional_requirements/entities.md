# Entities

## Mail Entity

### Description
The Mail entity represents an email message that can be either happy or gloomy in nature. The system will process these mails and send them to specified recipients based on their emotional content.

### Attributes
- **mailList**: String - A comma-separated list of email addresses to which the mail will be sent
- **content**: String - The content/body of the email message
- **subject**: String - The subject line of the email
- **createdAt**: DateTime - Timestamp when the mail entity was created
- **sentAt**: DateTime - Timestamp when the mail was successfully sent (nullable)

### Entity State
The entity uses `entity.meta.state` to track the current state of the mail in the workflow. The `isHappy` field mentioned in the user requirement is replaced by the entity state management system, where the state will indicate whether the mail is in a happy or gloomy processing state.

### Relationships
- No direct relationships with other entities in this simple application

### Notes
- The `isHappy` field from the original requirement is handled through the entity state system rather than as a direct attribute
- The system will automatically determine if a mail is happy or gloomy through criteria evaluation
- The `mailList` field should contain valid email addresses separated by commas
