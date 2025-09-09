# Entity Requirements

## ExampleEntity

### Description
The ExampleEntity represents a primary business object that demonstrates the core workflow functionality with processing and validation capabilities.

### Attributes
- `id` (string): Unique identifier for the entity (auto-generated)
- `name` (string): Name of the example entity
- `description` (string): Description of the entity
- `value` (number): Numeric value associated with the entity
- `category` (string): Category classification for the entity
- `isActive` (boolean): Flag indicating if the entity is active
- `createdAt` (string): Timestamp when the entity was created (ISO 8601 format)
- `updatedAt` (string): Timestamp when the entity was last updated (ISO 8601 format)
- `processedData` (object): Data that gets populated during processing
- `validationResult` (object): Result of validation checks

### Entity State
The entity state is managed internally by the workflow system and represents the current stage of the entity in its lifecycle:
- `none` (initial state)
- `created`
- `validated`
- `processed`
- `completed`

Note: The entity state is accessed via `entity.meta.state` and cannot be directly modified in the entity schema.

### Relationships
- **Updates**: OtherEntity (one-to-many relationship where ExampleEntity can update multiple OtherEntity instances)

## OtherEntity

### Description
The OtherEntity represents a secondary business object that gets updated by ExampleEntity processing and has its own simple workflow.

### Attributes
- `id` (string): Unique identifier for the entity (auto-generated)
- `title` (string): Title of the other entity
- `content` (string): Content or data of the entity
- `priority` (string): Priority level (LOW, MEDIUM, HIGH)
- `sourceEntityId` (string): Reference to the ExampleEntity that updated this entity
- `lastUpdatedBy` (string): Identifier of the entity that last updated this one
- `createdAt` (string): Timestamp when the entity was created (ISO 8601 format)
- `updatedAt` (string): Timestamp when the entity was last updated (ISO 8601 format)
- `metadata` (object): Additional metadata about the entity

### Entity State
The entity state is managed internally by the workflow system:
- `none` (initial state)
- `pending`
- `active`
- `archived`

Note: The entity state is accessed via `entity.meta.state` and cannot be directly modified in the entity schema.

### Relationships
- **Updated by**: ExampleEntity (many-to-one relationship where multiple OtherEntity instances can be updated by one ExampleEntity)
