# Employee API Routes

## Base Path: `/api/employees`

### Create Employee
- **POST** `/api/employees`
- **Request Body**:
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@company.com",
  "phone": "+1-555-0123",
  "hire_date": "2024-01-15",
  "position_id": "pos-123",
  "department": "Engineering"
}
```
- **Response**:
```json
{
  "id": "emp-789",
  "employee_id": "EMP-2024-001",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@company.com",
  "phone": "+1-555-0123",
  "hire_date": "2024-01-15",
  "position_id": "pos-123",
  "department": "Engineering",
  "is_active": false,
  "meta": {"state": "onboarding"}
}
```

### Get Employee
- **GET** `/api/employees/{id}`
- **Response**: Employee object with current state

### Update Employee
- **PUT** `/api/employees/{id}`
- **Request Body**: Employee fields to update + optional transition
```json
{
  "phone": "+1-555-9999",
  "user_id": "user-456",
  "transition": "complete_onboarding"
}
```

### List Employees
- **GET** `/api/employees`
- **Query Parameters**: `page`, `limit`, `state`, `position_id`, `department`
- **Response**: Paginated list of employees

### Delete Employee
- **DELETE** `/api/employees/{id}`

### Employee Transitions
- **POST** `/api/employees/{id}/transitions`
- **Request Body**:
```json
{
  "transition": "complete_onboarding"
}
```
