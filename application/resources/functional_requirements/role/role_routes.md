# Role API Routes

## Base Path: `/api/roles`

### Create Role
- **POST** `/api/roles`
- **Request Body**:
```json
{
  "name": "Manager",
  "description": "Management role with team oversight",
  "permission_ids": ["perm-123", "perm-456"]
}
```
- **Response**:
```json
{
  "id": "role-789",
  "name": "Manager",
  "description": "Management role with team oversight",
  "permission_ids": ["perm-123", "perm-456"],
  "is_active": false,
  "meta": {"state": "draft"}
}
```

### Get Role
- **GET** `/api/roles/{id}`
- **Response**: Role object with current state

### Update Role
- **PUT** `/api/roles/{id}`
- **Request Body**: Role fields to update + optional transition
```json
{
  "description": "Updated description",
  "permission_ids": ["perm-123", "perm-456", "perm-789"],
  "transition": "activate_role"
}
```

### List Roles
- **GET** `/api/roles`
- **Query Parameters**: `page`, `limit`, `state`, `active_only`
- **Response**: Paginated list of roles

### Delete Role
- **DELETE** `/api/roles/{id}`

### Role Transitions
- **POST** `/api/roles/{id}/transitions`
- **Request Body**:
```json
{
  "transition": "activate_role"
}
```
