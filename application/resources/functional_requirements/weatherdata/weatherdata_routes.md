# WeatherData Routes

## Base Path: `/api/weather`

## Endpoints

### POST /api/weather
Fetch weather data for subscription
- **Transition**: start_fetch
- **Request**:
```json
{
  "subscription_id": "sub-456",
  "forecast_date": "2024-01-15"
}
```
- **Response**:
```json
{
  "id": "weather-789",
  "subscription_id": "sub-456",
  "location": "Toronto, ON, Canada",
  "latitude": 43.6532,
  "longitude": -79.3832,
  "fetch_timestamp": "2024-01-15T06:00:00Z",
  "forecast_date": "2024-01-15",
  "state": "fetching"
}
```

### PUT /api/weather/{id}
Update weather data processing
- **Transition**: process_data, prepare_notification, expire_data
- **Request**:
```json
{
  "transition": "process_data",
  "temperature": 5.2,
  "humidity": 65,
  "wind_speed": 15,
  "weather_condition": "Partly Cloudy"
}
```
- **Response**:
```json
{
  "id": "weather-789",
  "subscription_id": "sub-456",
  "location": "Toronto, ON, Canada",
  "temperature": 5.2,
  "humidity": 65,
  "wind_speed": 15,
  "weather_condition": "Partly Cloudy",
  "fetch_timestamp": "2024-01-15T06:00:00Z",
  "forecast_date": "2024-01-15",
  "state": "processed"
}
```

### GET /api/weather/{id}
Get weather data details
- **Response**:
```json
{
  "id": "weather-789",
  "subscription_id": "sub-456",
  "location": "Toronto, ON, Canada",
  "temperature": 5.2,
  "humidity": 65,
  "wind_speed": 15,
  "weather_condition": "Partly Cloudy",
  "fetch_timestamp": "2024-01-15T06:00:00Z",
  "forecast_date": "2024-01-15",
  "state": "notification_ready"
}
```

### GET /api/subscriptions/{subscription_id}/weather
Get weather data for subscription
- **Response**:
```json
[
  {
    "id": "weather-789",
    "temperature": 5.2,
    "humidity": 65,
    "wind_speed": 15,
    "weather_condition": "Partly Cloudy",
    "forecast_date": "2024-01-15",
    "state": "notification_ready"
  }
]
```
