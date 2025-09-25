# Category Workflow

## Workflow States and Transitions

### States:
- `initial_state`: Starting state
- `active`: Category is active and available

### Transitions:

```mermaid
stateDiagram-v2
    [*] --> initial_state
    initial_state --> active : create_category (auto)
    active --> [*]
```

### Workflow Rules:
- Simple workflow with automatic transition to active state
- No manual transitions needed for basic reference entity

## Processors

### CreateCategoryProcessor
- **Entity**: Category
- **Purpose**: Initialize category data
- **Input**: Category entity with name
- **Output**: Category entity ready for use
- **Pseudocode**:
```
process(entity):
    validate_category_name(entity.name)
    entity.createdAt = current_timestamp()
    return entity
```

## Criteria

### CategoryValidityCriterion
- **Purpose**: Check if category data is valid
- **Pseudocode**:
```
check(entity):
    return entity.name != null and entity.name.length > 0
```
