# User Entity Requirements

## Entity: User

**Purpose**: Represents customers and users of the Purrfect Pets system.

**Attributes**:
- `id`: Unique identifier (integer)
- `username`: Unique username (string)
- `firstName`: User's first name (string)
- `lastName`: User's last name (string)
- `email`: Email address (string)
- `password`: Encrypted password (string)
- `phone`: Phone number (string)
- `userStatus`: User account status (integer)

**Relationships**:
- May have many Orders (implied)

**Business Rules**:
- Username must be unique
- Email validation required
- Password must be encrypted
- UserStatus controls account access
