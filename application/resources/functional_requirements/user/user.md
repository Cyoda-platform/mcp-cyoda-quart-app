# User Entity

## Description
Represents system users with authentication credentials and role assignments.

## Attributes
- **username**: Unique identifier for login (string, required)
- **email**: User email address (string, required, unique)
- **password_hash**: Encrypted password (string, required)
- **first_name**: User's first name (string, required)
- **last_name**: User's last name (string, required)
- **is_active**: Account status (boolean, default: true)
- **role_ids**: Array of assigned role IDs (array of strings)
- **created_at**: Account creation timestamp (datetime)
- **last_login**: Last login timestamp (datetime, nullable)

## Relationships
- **Many-to-Many with Role**: Users can have multiple roles
- **One-to-One with Employee**: Each employee has one user account

## Business Rules
- Username and email must be unique
- Password must meet security requirements
- Active users can authenticate and access system
- Inactive users cannot login
