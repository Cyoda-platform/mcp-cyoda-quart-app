# Cyoda Application End-to-End Testing Guide

## Overview
This guide provides step-by-step instructions for running and testing the Cyoda client application end-to-end, including workflow import, entity creation, and verification of processor/criteria execution.

## Important Observations
⚠️ **Critical**: When importing workflows, use the **exact entity name** as defined in the entity model's `ENTITY_NAME` constant, not lowercase versions. For example:
- If `ENTITY_NAME = "OtherEntity"` → import workflow with entity name `"OtherEntity"`
- If `ENTITY_NAME = "ExampleEntity"` → import workflow with entity name `"ExampleEntity"`

## Prerequisites
1. Cyoda server running and accessible
2. Valid authentication credentials in `.env` file
3. Python virtual environment activated (`.venv`)

## Step-by-Step Testing Process

### 1. Start the Application
```bash
# From project root
python run_app.py
```

**Expected Output:**
```
INFO:common.processor.manager:Registered processor: ExampleEntityProcessor (ExampleEntityProcessor)
INFO:common.processor.manager:Registered criteria: ExampleEntityValidationCriterion (ExampleEntityValidationCriterion)
INFO:common.grpc_client.handlers.greet:Received greet event: {...}
```

### 2. Import Required Workflows

#### Import ExampleEntity Workflow
```python
workflow_mgmt_import_workflows_from_file_tool_cyoda-mcp(
    entity_name="ExampleEntity",  # Use exact ENTITY_NAME from model
    model_version="1",
    file_path="example_application/resources/workflow/exampleentity/version_1/ExampleEntity.json",
    import_mode="REPLACE"
)
```

#### Import OtherEntity Workflow (Required for Processor)
```python
workflow_mgmt_import_workflows_from_file_tool_cyoda-mcp(
    entity_name="OtherEntity",  # Use exact ENTITY_NAME from model
    model_version="1",
    file_path="example_application/resources/workflow/otherentity/version_1/OtherEntity.json",
    import_mode="REPLACE"
)
```

**Expected Output:** `{"success":true,"workflows_imported":1}`

### 3. Create Test Entity

Create an ExampleEntity with valid data that will pass criteria validation:

```python
entity_create_entity_tool_cyoda-mcp(
    entity_model="exampleentity",  # Use lowercase for API calls
    entity_data={
        "name": "End-to-End Test Entity",
        "description": "Testing complete workflow execution",
        "value": 150,
        "category": "ELECTRONICS",  # Must be valid category from criteria
        "isActive": true
    }
)
```

### 4. Monitor Application Logs

Watch for the complete workflow execution sequence:

#### ✅ Criteria Validation
```
INFO:example_application.criterion.example_entity_validation_criterion.ExampleEntityValidationCriterion:Validating entity [entity-id]
INFO:example_application.criterion.example_entity_validation_criterion.ExampleEntityValidationCriterion:Entity [entity-id] passed all validation criteria
```

#### ✅ Processor Execution
```
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:Processing ExampleEntity [entity-id]
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:Created OtherEntity [other-entity-id] (index 1)
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:Created OtherEntity [other-entity-id] (index 2)
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:Created OtherEntity [other-entity-id] (index 3)
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:ExampleEntity [entity-id] processed successfully
```

#### ✅ gRPC Communication
```
INFO:common.grpc_client.middleware.logging:[IN] Received event - Type: EntityCriteriaCalculationRequest
INFO:common.grpc_client.middleware.logging:[IN] Received event - Type: EntityProcessorCalculationRequest
INFO:common.grpc_client.outbox:[OUT] Sending event - Type: EntityCriteriaCalculationResponse
INFO:common.grpc_client.outbox:[OUT] Sending event - Type: EntityProcessorCalculationResponse
```

### 5. Verification Checklist

- [ ] Application starts without errors
- [ ] Processor and criteria are registered
- [ ] gRPC connection established (greet event received)
- [ ] Workflows imported successfully
- [ ] Entity creation triggers criteria validation
- [ ] Criteria validation passes and logs to stdout
- [ ] Processor execution triggered after criteria pass
- [ ] Processor creates 3 OtherEntity instances successfully
- [ ] Processor completes without errors
- [ ] All gRPC responses sent successfully

## Common Issues and Solutions

### Issue: Entity Name Mismatch
**Symptoms:** Workflow not found, entity creation fails
**Solution:** Ensure entity model `ENTITY_NAME` matches workflow import name exactly

### Issue: Criteria Validation Fails
**Symptoms:** Processor not triggered
**Solution:** Check entity data meets validation rules:
- Valid categories: `["ELECTRONICS", "CLOTHING", "BOOKS", "HOME", "SPORTS"]`
- Name length: 3-100 characters
- Value > 0
- Description < 500 characters

### Issue: OtherEntity Creation Fails
**Symptoms:** HTTP 500 errors in processor
**Solution:** Ensure OtherEntity workflow is imported with correct entity name

### Issue: Workflow Transition Errors
**Symptoms:** State machine transition failures
**Solution:** Let Cyoda workflow engine handle transitions automatically (don't force manual transitions)

## File Structure Reference

```
├── example_application/          # Example code - users add their code to application/
│   ├── entity/
│   │   ├── example_entity.py     # ENTITY_NAME = "exampleentity"
│   │   └── other_entity.py       # ENTITY_NAME = "otherentity"
│   ├── processor/
│   │   └── example_entity_processor.py
│   ├── criterion/
│   │   └── example_entity_validation_criterion.py
│   └── resources/workflow/
│       ├── exampleentity/version_1/ExampleEntity.json
│       └── otherentity/version_1/OtherEntity.json
├── application/                  # User code directory (empty by default)
├── common/
│   └── entity/
│       └── cyoda_entity.py
└── services/
    └── config.py                 # Processor modules: ["example_application.processor", "example_application.criterion"]
```

## Success Criteria

The end-to-end test is successful when:
1. No errors in application startup
2. Both workflows imported successfully
3. Entity creation triggers complete workflow
4. Criteria validation executes and logs
5. Processor executes and logs
6. 3 OtherEntity instances created successfully
7. All gRPC communication completes successfully

This confirms the complete Cyoda client application is working correctly with proper workflow processing, entity management, and gRPC communication.
