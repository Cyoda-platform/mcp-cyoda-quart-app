# SPA Admin System - Functional Requirements Summary

## Overview
This document summarizes the functional requirements for a small Single Page Application (SPA) with an admin menu for managing roles, permissions, users, employees, and positions. The system provides comprehensive user management with role-based access control and employee management capabilities.

## Entities Created

### 1. User Entity
- **Purpose**: System authentication and access control
- **Key Attributes**: username, email, password_hash, first_name, last_name, role_ids
- **Workflow States**: initial_state → pending → active → suspended/inactive
- **Key Features**: Role assignment, account activation, suspension capabilities

### 2. Role Entity  
- **Purpose**: Group permissions for access control
- **Key Attributes**: name, description, permission_ids
- **Workflow States**: initial_state → draft → active → inactive
- **Key Features**: Permission grouping, role activation with validation

### 3. Permission Entity
- **Purpose**: Define specific access rights and capabilities
- **Key Attributes**: name, description, resource, action
- **Workflow States**: initial_state → active → inactive
- **Key Features**: Resource-action based permissions, system permission protection

### 4. Employee Entity
- **Purpose**: Staff member management and information
- **Key Attributes**: employee_id, first_name, last_name, email, position_id, user_id
- **Workflow States**: initial_state → onboarding → active → on_leave/terminated
- **Key Features**: Position assignment, user account linking, leave management

### 5. Position Entity
- **Purpose**: Job positions and organizational structure
- **Key Attributes**: title, description, department, level, salary_range
- **Workflow States**: initial_state → active → inactive
- **Key Features**: Department organization, salary range management, employee assignment validation

## Entity Relationships

### Core Relationships
- **User ↔ Role**: Many-to-Many (Users can have multiple roles)
- **Role ↔ Permission**: Many-to-Many (Roles can have multiple permissions)
- **Employee ↔ User**: One-to-One (Each employee can have one user account)
- **Employee ↔ Position**: Many-to-One (Multiple employees can have same position)

### Business Logic
- Users authenticate and access system based on assigned roles
- Roles define what permissions users have
- Employees are staff members who may or may not have user accounts
- Positions define job roles and can be assigned to multiple employees

## Workflow Summary

### User Workflow (4 processors, 0 criteria)
- **CreateUserProcessor**: Initialize user account with pending status
- **ActivateUserProcessor**: Activate user for login access
- **SuspendUserProcessor**: Temporarily disable user access
- **ReactivateUserProcessor**: Restore suspended user access
- **DeactivateUserProcessor**: Permanently disable user account

### Role Workflow (3 processors, 1 criteria)
- **CreateRoleProcessor**: Initialize role in draft state
- **ActivateRoleProcessor**: Activate role for assignment (requires validation)
- **DeactivateRoleProcessor**: Disable role from assignment
- **ReactivateRoleProcessor**: Reactivate disabled role
- **ValidateRolePermissions**: Ensure role has valid permissions before activation

### Permission Workflow (3 processors, 0 criteria)
- **CreatePermissionProcessor**: Create and activate permission
- **DeactivatePermissionProcessor**: Disable permission and remove from roles
- **ReactivatePermissionProcessor**: Reactivate disabled permission

### Employee Workflow (4 processors, 1 criteria)
- **CreateEmployeeProcessor**: Initialize employee record in onboarding
- **CompleteOnboardingProcessor**: Activate employee after setup completion
- **StartLeaveProcessor**: Put employee on temporary leave
- **ReturnFromLeaveProcessor**: Return employee from leave
- **TerminateEmployeeProcessor**: Terminate employee and cleanup
- **ValidateEmployeeSetup**: Ensure required setup before activation

### Position Workflow (3 processors, 1 criteria)
- **CreatePositionProcessor**: Create and activate position
- **DeactivatePositionProcessor**: Disable position (requires no active employees)
- **ReactivatePositionProcessor**: Reactivate disabled position
- **ValidateNoActiveEmployees**: Ensure no active employees before deactivation

## API Endpoints Summary

### User Management (`/api/users`)
- CRUD operations with state transitions
- Role assignment and user activation
- Authentication and access control

### Role Management (`/api/roles`)
- Role creation and permission assignment
- Role activation with validation
- User role assignment capabilities

### Permission Management (`/api/permissions`)
- System permission definition
- Resource-action based access control
- Role permission assignment

### Employee Management (`/api/employees`)
- Employee onboarding and lifecycle
- Position assignment and user linking
- Leave and termination management

### Position Management (`/api/positions`)
- Organizational structure definition
- Department and level management
- Employee assignment validation

## Key Business Rules

1. **Security**: All passwords are hashed, unique usernames/emails required
2. **Access Control**: Role-based permissions with resource-action model
3. **Data Integrity**: Referential integrity between entities maintained
4. **Workflow Validation**: State transitions validated with business criteria
5. **Employee Lifecycle**: Complete onboarding process with position assignment
6. **System Protection**: Core permissions and admin roles cannot be deleted

## Files Created

### Entity Requirements (5 files)
- `user/user.md` - User entity specification
- `role/role.md` - Role entity specification  
- `permission/permission.md` - Permission entity specification
- `employee/employee.md` - Employee entity specification
- `position/position.md` - Position entity specification

### Workflow Definitions (5 files)
- `user/user_workflow.md` - User workflow with state diagram
- `role/role_workflow.md` - Role workflow with state diagram
- `permission/permission_workflow.md` - Permission workflow with state diagram
- `employee/employee_workflow.md` - Employee workflow with state diagram
- `position/position_workflow.md` - Position workflow with state diagram

### Workflow JSON (5 files)
- `application/resources/workflow/user/version_1/User.json`
- `application/resources/workflow/role/version_1/Role.json`
- `application/resources/workflow/permission/version_1/Permission.json`
- `application/resources/workflow/employee/version_1/Employee.json`
- `application/resources/workflow/position/version_1/Position.json`

### API Routes (5 files)
- `user/user_routes.md` - User API endpoints
- `role/role_routes.md` - Role API endpoints
- `permission/permission_routes.md` - Permission API endpoints
- `employee/employee_routes.md` - Employee API endpoints
- `position/position_routes.md` - Position API endpoints

## Next Steps

1. **Implementation**: Implement the workflow processors and criteria functions
2. **API Development**: Build the REST API endpoints as specified
3. **Frontend Development**: Create the SPA with Tailwind CSS for the admin interface
4. **Testing**: Develop comprehensive tests for all entities and workflows
5. **Deployment**: Deploy the complete system with proper security measures

This system provides a complete foundation for an admin SPA with comprehensive user, role, permission, employee, and position management capabilities.
