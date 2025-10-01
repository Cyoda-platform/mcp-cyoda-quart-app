# Employee Entity

## Description
Represents staff members with personal and professional information.

## Attributes
- **employee_id**: Unique employee identifier (string, required, unique)
- **first_name**: Employee's first name (string, required)
- **last_name**: Employee's last name (string, required)
- **email**: Employee email address (string, required, unique)
- **phone**: Phone number (string, optional)
- **hire_date**: Employment start date (date, required)
- **position_id**: Assigned position ID (string, required)
- **user_id**: Associated user account ID (string, optional)
- **department**: Department name (string, optional)
- **is_active**: Employment status (boolean, default: true)

## Relationships
- **Many-to-One with Position**: Employee belongs to one position
- **One-to-One with User**: Employee can have one user account

## Business Rules
- Employee ID and email must be unique
- Active employees can be assigned user accounts
- Position assignment is required for active employees
