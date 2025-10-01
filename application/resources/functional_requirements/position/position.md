# Position Entity

## Description
Represents job positions and titles within the organization.

## Attributes
- **title**: Position title (string, required, unique)
- **description**: Position description (string, required)
- **department**: Department name (string, required)
- **level**: Position level/grade (string, optional)
- **salary_range_min**: Minimum salary (number, optional)
- **salary_range_max**: Maximum salary (number, optional)
- **is_active**: Position status (boolean, default: true)
- **created_at**: Position creation timestamp (datetime)
- **updated_at**: Last modification timestamp (datetime)

## Relationships
- **One-to-Many with Employee**: Position can have multiple employees

## Business Rules
- Position titles must be unique within department
- Active positions can be assigned to employees
- Salary range minimum must be less than maximum
- Positions with assigned employees cannot be deleted
