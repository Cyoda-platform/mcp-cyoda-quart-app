# EmailNotification Entity

## Description
Manages email notifications for weather updates sent to users.

## Attributes
- **user_id**: Reference to User entity (required)
- **weather_data_id**: Reference to WeatherData entity (required)
- **recipient_email**: Email address to send notification (required)
- **subject**: Email subject line (required)
- **content**: Email body content (required)
- **sent_timestamp**: When email was sent (nullable)
- **delivery_status**: Email delivery status (pending, sent, failed) (default: pending)
- **retry_count**: Number of send attempts (default: 0)

## Relationships
- Belongs to User
- Belongs to WeatherData

## Business Rules
- Maximum 3 retry attempts for failed emails
- Content includes weather data and location information
- Subject includes location and date
- Only sent to active users
