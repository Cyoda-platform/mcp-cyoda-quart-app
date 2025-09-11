# Entities

## Mail Entity

### Description
The Mail entity represents an email that can be either happy or gloomy in nature. It contains information about the happiness state and the list of recipients.

### Attributes
- **isHappy** (boolean): Indicates whether the mail content is happy (true) or gloomy (false)
- **mailList** (array of strings): List of email addresses to send the mail to

### Relationships
- No direct relationships with other entities (standalone entity)

### Entity State
The Mail entity uses the internal `entity.meta.state` to track its workflow state. The state is managed automatically by the system based on workflow transitions and cannot be modified directly by processors.

### Notes
- The `isHappy` field determines the type of mail content to be sent
- The `mailList` field must contain valid email addresses
- Entity state transitions are handled automatically by the workflow system
