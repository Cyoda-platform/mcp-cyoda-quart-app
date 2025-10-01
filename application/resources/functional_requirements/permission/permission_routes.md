# Permission API Routes

## Base Path: `/api/permissions`

### Create Permission
- **POST** `/api/permissions`
- **Request Body**:
```json
{
  "name": "user.create",
  "description": "Create new users",
  "resource": "user",
  "action": "create"
}
```
- **Response**:
```json
{
  "id": "perm-789",
  "name": "user.create",
  "description": "Create new users",
  "resource": "user",
  "action": "create",
  "is_active": true,
  "meta": {"state": "active"}
}
```

### Get Permission
- **GET** `/api/permissions/{id}`
- **Response**: Permission object with current state

### Update Permission
- **PUT** `/api/permissions/{id}`
- **Request Body**: Permission fields to update + optional transition
```json
{
  "description": "Updated description",
  "transition": "deactivate_permission"
}
```

### List Permissions
- **GET** `/api/permissions`
- **Query Parameters**: `page`, `limit`, `state`, `resource`, `action`
- **Response**: Paginated list of permissions

### Delete Permission
- **DELETE** `/api/permissions/{id}`

### Permission Transitions
- **POST** `/api/permissions/{id}/transitions`
- **Request Body**:
```json
{
  "transition": "deactivate_permission"
}
```
