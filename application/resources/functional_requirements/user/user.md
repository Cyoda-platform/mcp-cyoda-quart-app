# User Entity Requirements

## Entity: User

**Purpose**: Represents customers and users of the Purrfect Pets store.

## Attributes

- **username** (string, required): Unique username for login
- **firstName** (string): User's first name
- **lastName** (string): User's last name
- **email** (string, required): User's email address
- **phone** (string): User's phone number
- **password** (string): Encrypted password (not exposed in API responses)
- **preferences** (object): User preferences for pet types, notifications

## Relationships

- **Orders**: One user can have multiple orders
- **Favorites**: Users can favorite multiple pets

## State Management

User account status is managed through `entity.meta.state`:
- **registered**: User has registered but not verified email
- **active**: User account is active and verified
- **suspended**: User account is temporarily suspended

Note: The original Petstore API "userStatus" field maps to `entity.meta.state` for workflow management.
