# Entities

## EggAlarm

The EggAlarm entity represents an alarm set by a user for cooking eggs.

### Attributes

- **id**: String - Unique identifier for the alarm
- **userId**: String - Identifier of the user who created the alarm
- **eggType**: String - Type of egg cooking (SOFT_BOILED, MEDIUM_BOILED, HARD_BOILED)
- **duration**: Integer - Cooking duration in seconds
- **createdAt**: DateTime - When the alarm was created
- **scheduledTime**: DateTime - When the alarm is scheduled to go off
- **title**: String - Optional title for the alarm (defaults to egg type)
- **isActive**: Boolean - Whether the alarm is currently active

### Relationships

- **User**: Many-to-One relationship with User entity (one user can have multiple alarms)

### Entity State

The entity state represents the current status of the alarm in its lifecycle:
- **CREATED**: Alarm has been created but not yet started
- **ACTIVE**: Alarm is currently running/counting down
- **COMPLETED**: Alarm has finished and notification was sent
- **CANCELLED**: Alarm was cancelled by the user
- **EXPIRED**: Alarm time has passed without being acknowledged

Note: The state field is managed automatically by the workflow system and can be accessed via `entity.meta.state` but cannot be directly modified.

## User

The User entity represents a user of the Egg Alarm application.

### Attributes

- **id**: String - Unique identifier for the user
- **username**: String - User's chosen username
- **email**: String - User's email address
- **createdAt**: DateTime - When the user account was created
- **preferences**: Object - User preferences for default alarm settings

### Relationships

- **EggAlarms**: One-to-Many relationship with EggAlarm entity (one user can have multiple alarms)

### Entity State

The entity state represents the current status of the user account:
- **REGISTERED**: User has been registered but not yet verified
- **ACTIVE**: User account is active and can use the application
- **SUSPENDED**: User account has been temporarily suspended
- **DELETED**: User account has been marked for deletion

Note: The state field is managed automatically by the workflow system and can be accessed via `entity.meta.state` but cannot be directly modified.
