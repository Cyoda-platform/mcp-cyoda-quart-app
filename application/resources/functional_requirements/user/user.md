# User Entity

## Description
Manages user information and email preferences for weather notifications.

## Attributes
- **email**: User's email address (required, unique)
- **name**: User's display name (optional)
- **timezone**: User's timezone for scheduling notifications (default: UTC)
- **notification_time**: Preferred time for daily notifications (default: 08:00)
- **active**: Whether user account is active (default: true)

## Relationships
- Has many WeatherSubscriptions
- Has many EmailNotifications

## Business Rules
- Email must be valid format
- Only active users receive notifications
- Notification time stored in 24-hour format
