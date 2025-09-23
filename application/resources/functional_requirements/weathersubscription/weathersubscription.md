# WeatherSubscription Entity

## Description
Manages user subscriptions to weather updates for specific locations.

## Attributes
- **user_id**: Reference to User entity (required)
- **location**: Geographic location (city, province/state, country) (required)
- **latitude**: Location latitude for API calls (required)
- **longitude**: Location longitude for API calls (required)
- **frequency**: Notification frequency (daily, weekly) (default: daily)
- **active**: Whether subscription is active (default: true)

## Relationships
- Belongs to User
- Has many WeatherData records
- Has many EmailNotifications

## Business Rules
- User can have multiple subscriptions for different locations
- Only active subscriptions generate notifications
- Location coordinates must be valid (lat: -90 to 90, lng: -180 to 180)
