# WeatherData Entity

## Description
Stores weather information fetched from MSC GeoMet API for specific locations.

## Attributes
- **subscription_id**: Reference to WeatherSubscription (required)
- **location**: Geographic location (required)
- **latitude**: Location latitude (required)
- **longitude**: Location longitude (required)
- **temperature**: Temperature in Celsius (required)
- **humidity**: Humidity percentage (required)
- **wind_speed**: Wind speed in km/h (required)
- **weather_condition**: Weather description (e.g., "Sunny", "Cloudy") (required)
- **fetch_timestamp**: When data was fetched from API (required)
- **forecast_date**: Date for which weather is forecasted (required)

## Relationships
- Belongs to WeatherSubscription
- Has many EmailNotifications

## Business Rules
- Data must be fetched from MSC GeoMet API
- Temperature stored in Celsius
- Wind speed stored in km/h
- Data expires after 24 hours
