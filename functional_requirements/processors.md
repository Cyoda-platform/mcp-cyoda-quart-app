# Processor Requirements

## ExampleEntityProcessor

### Description
The ExampleEntityProcessor handles the main business logic for processing ExampleEntity instances. It enriches the entity data, performs calculations, and updates related OtherEntity instances.

### Entity
ExampleEntity

### Expected Input Data
- ExampleEntity in `validated` state
- Entity must have:
  - `name` (non-empty string)
  - `value` (positive number)
  - `category` (valid category string)
  - `isActive` (boolean)

### Process Logic (Pseudocode)

```
process(entity):
    // Validate input entity state
    if entity.meta.state != "validated":
        throw error "Entity must be in validated state"
    
    // Enrich entity with processed data
    entity.processedData = {
        processedAt: current_timestamp(),
        calculatedValue: entity.value * 2.5,
        enrichedCategory: entity.category.toUpperCase() + "_PROCESSED",
        processingId: generate_unique_id()
    }
    
    // Update entity timestamps
    entity.updatedAt = current_timestamp()
    
    // Create or update related OtherEntity instances
    for i from 1 to 3:
        otherEntity = {
            title: entity.name + "_Related_" + i,
            content: "Generated from " + entity.name + " processing",
            priority: determine_priority(entity.value, i),
            sourceEntityId: entity.id,
            lastUpdatedBy: "ExampleEntityProcessor",
            createdAt: current_timestamp(),
            updatedAt: current_timestamp(),
            metadata: {
                sourceProcessingId: entity.processedData.processingId,
                generatedIndex: i,
                sourceCategory: entity.category
            }
        }
        
        // Create new OtherEntity and transition to active state
        create_other_entity(otherEntity)
        transition_other_entity_to_active(otherEntity.id)
    
    // Log processing completion
    log_info("ExampleEntity " + entity.id + " processed successfully")
    
    return entity

determine_priority(value, index):
    if value > 100 and index == 1:
        return "HIGH"
    else if value > 50:
        return "MEDIUM"
    else:
        return "LOW"
```

### Expected Entity Output
- ExampleEntity with updated `processedData` object
- ExampleEntity with updated `updatedAt` timestamp
- Entity state remains in `validated` (will be transitioned by workflow)

### Other Entity Updates
- Creates 3 new OtherEntity instances
- Each OtherEntity is transitioned to `active` state using `transition_to_active` transition
- OtherEntity instances are linked to the source ExampleEntity via `sourceEntityId`

### Error Handling
- Validates entity state before processing
- Handles failures in OtherEntity creation gracefully
- Logs all processing steps for audit trail
