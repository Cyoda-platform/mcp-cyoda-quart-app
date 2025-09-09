# Controller Requirements

## ExampleEntityRoutes

### Description
REST API endpoints for managing ExampleEntity instances with workflow integration.

### Base Path
`/api/example-entities`

### Endpoints

#### 1. Create ExampleEntity
- **Method**: POST
- **Path**: `/api/example-entities`
- **Description**: Creates a new ExampleEntity

**Request Body Example**:
```json
{
  "name": "Sample Product",
  "description": "This is a sample product for demonstration",
  "value": 25.99,
  "category": "ELECTRONICS",
  "isActive": true
}
```

**Response Example**:
```json
{
  "id": "example-entity-123",
  "message": "ExampleEntity created successfully"
}
```

#### 2. Get ExampleEntity by ID
- **Method**: GET
- **Path**: `/api/example-entities/{id}`
- **Description**: Retrieves a specific ExampleEntity by ID

**Response Example**:
```json
{
  "id": "example-entity-123",
  "name": "Sample Product",
  "description": "This is a sample product for demonstration",
  "value": 25.99,
  "category": "ELECTRONICS",
  "isActive": true,
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:30:00Z",
  "state": "created"
}
```

#### 3. List ExampleEntities
- **Method**: GET
- **Path**: `/api/example-entities`
- **Description**: Retrieves all ExampleEntity instances

**Query Parameters**:
- `category` (optional): Filter by category
- `isActive` (optional): Filter by active status
- `state` (optional): Filter by workflow state

**Response Example**:
```json
{
  "entities": [
    {
      "id": "example-entity-123",
      "name": "Sample Product",
      "state": "created"
    }
  ],
  "total": 1
}
```

#### 4. Update ExampleEntity
- **Method**: PUT
- **Path**: `/api/example-entities/{id}`
- **Description**: Updates an ExampleEntity and optionally triggers a workflow transition

**Query Parameters**:
- `transition` (optional): Name of the workflow transition to trigger

**Request Body Example**:
```json
{
  "name": "Updated Sample Product",
  "description": "Updated description",
  "value": 35.99,
  "category": "ELECTRONICS",
  "isActive": true,
  "transition": "transition_to_validated"
}
```

**Response Example**:
```json
{
  "id": "example-entity-123",
  "message": "ExampleEntity updated successfully",
  "newState": "validated"
}
```

#### 5. Delete ExampleEntity
- **Method**: DELETE
- **Path**: `/api/example-entities/{id}`
- **Description**: Deletes an ExampleEntity

**Response Example**:
```json
{
  "message": "ExampleEntity deleted successfully"
}
```

#### 6. Trigger Workflow Transition
- **Method**: POST
- **Path**: `/api/example-entities/{id}/transitions`
- **Description**: Triggers a specific workflow transition

**Request Body Example**:
```json
{
  "transitionName": "transition_to_processed"
}
```

**Response Example**:
```json
{
  "id": "example-entity-123",
  "message": "Transition executed successfully",
  "previousState": "validated",
  "newState": "processed"
}
```

## OtherEntityRoutes

### Description
REST API endpoints for managing OtherEntity instances.

### Base Path
`/api/other-entities`

### Endpoints

#### 1. Create OtherEntity
- **Method**: POST
- **Path**: `/api/other-entities`
- **Description**: Creates a new OtherEntity

**Request Body Example**:
```json
{
  "title": "Related Entity 1",
  "content": "Content for the related entity",
  "priority": "MEDIUM",
  "sourceEntityId": "example-entity-123",
  "lastUpdatedBy": "user-123",
  "metadata": {
    "category": "generated",
    "source": "manual"
  }
}
```

**Response Example**:
```json
{
  "id": "other-entity-456",
  "message": "OtherEntity created successfully"
}
```

#### 2. Get OtherEntity by ID
- **Method**: GET
- **Path**: `/api/other-entities/{id}`
- **Description**: Retrieves a specific OtherEntity by ID

**Response Example**:
```json
{
  "id": "other-entity-456",
  "title": "Related Entity 1",
  "content": "Content for the related entity",
  "priority": "MEDIUM",
  "sourceEntityId": "example-entity-123",
  "lastUpdatedBy": "user-123",
  "createdAt": "2024-01-15T10:35:00Z",
  "updatedAt": "2024-01-15T10:35:00Z",
  "state": "pending"
}
```

#### 3. List OtherEntities
- **Method**: GET
- **Path**: `/api/other-entities`
- **Description**: Retrieves all OtherEntity instances

**Query Parameters**:
- `sourceEntityId` (optional): Filter by source entity ID
- `priority` (optional): Filter by priority level
- `state` (optional): Filter by workflow state

**Response Example**:
```json
{
  "entities": [
    {
      "id": "other-entity-456",
      "title": "Related Entity 1",
      "priority": "MEDIUM",
      "state": "pending"
    }
  ],
  "total": 1
}
```

#### 4. Update OtherEntity
- **Method**: PUT
- **Path**: `/api/other-entities/{id}`
- **Description**: Updates an OtherEntity and optionally triggers a workflow transition

**Query Parameters**:
- `transition` (optional): Name of the workflow transition to trigger

**Request Body Example**:
```json
{
  "title": "Updated Related Entity",
  "content": "Updated content",
  "priority": "HIGH",
  "lastUpdatedBy": "user-456",
  "transition": "transition_to_active"
}
```

**Response Example**:
```json
{
  "id": "other-entity-456",
  "message": "OtherEntity updated successfully",
  "newState": "active"
}
```

#### 5. Delete OtherEntity
- **Method**: DELETE
- **Path**: `/api/other-entities/{id}`
- **Description**: Deletes an OtherEntity

**Response Example**:
```json
{
  "message": "OtherEntity deleted successfully"
}
```
