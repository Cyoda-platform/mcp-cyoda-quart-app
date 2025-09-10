# AI Testing Guide for Contributors

This guide provides specific commands and prompts for working with AI assistants to test the Cyoda Client Application.

## 🤖 AI Assistant Commands

### Quick Start Commands

#### 1. Run Complete E2E Test
```
"Please run end-to-end tests for the Cyoda client application using MCP tools. Import both ExampleEntity and OtherEntity workflows, create test entities, and verify complete workflow execution with processor and criteria logging."
```

#### 2. Code Quality Check
```
"Run all code quality tools (black, isort, mypy, flake8, bandit) on the Cyoda project and fix any issues found."
```

#### 3. Integration Test Verification
```
"Run the integration test suite (tests/integration/test_grpc_handlers_e2e.py) and confirm all 12 tests pass."
```

#### 4. Application Health Check
```
"Start the Cyoda application and verify that processors and criteria are registered correctly, then check gRPC connectivity."
```

## 📋 Detailed Testing Workflows

### Full E2E Workflow Test

**Step 1: Request Full Test**
```
"I need you to test the complete Cyoda client application workflow:

1. Start the application (python run_app.py)
2. Import ExampleEntity workflow from example_application/resources/workflow/exampleentity/version_1/ExampleEntity.json
3. Import OtherEntity workflow from example_application/resources/workflow/otherentity/version_1/OtherEntity.json  
4. Create an ExampleEntity with valid data
5. Verify in logs that criteria validation executes
6. Verify in logs that processor executes and creates 3 OtherEntity instances
7. Confirm all gRPC events are processed successfully"
```

**Expected AI Response Pattern:**
- ✅ Application starts with processor/criteria registration
- ✅ Both workflows import successfully
- ✅ Entity creation triggers workflow
- ✅ Logs show criteria validation
- ✅ Logs show processor creating 3 OtherEntity instances
- ✅ All gRPC communication completes

### Code Quality Verification

**Request:**
```
"Please run all code quality checks for the Cyoda project and ensure everything passes:
- black (code formatting)
- isort (import sorting)  
- mypy (type checking)
- flake8 (style checking)
- bandit (security scanning)
- pytest (all tests)

Fix any issues found and confirm all checks pass."
```

**Expected Results:**
- All formatters run without changes needed
- No type errors from mypy
- No style violations from flake8
- No security issues from bandit
- All tests pass (12/12 integration tests)

### Performance and Load Testing

**Request:**
```
"Test the Cyoda application performance by creating multiple ExampleEntity instances rapidly and verify:
1. All entities are processed correctly
2. Each entity triggers processor to create 3 OtherEntity instances
3. No errors or timeouts occur
4. gRPC communication remains stable
5. Application logs show successful processing for all entities"
```

## 🔍 Verification Checklist

### Application Startup ✅
- [ ] Application starts without errors
- [ ] Processor registered: `ExampleEntityProcessor`
- [ ] Criteria registered: `ExampleEntityValidationCriterion`
- [ ] gRPC connection established
- [ ] Entity discovery finds 4 entity class mappings

### Workflow Import ✅
- [ ] ExampleEntity workflow imports successfully
- [ ] OtherEntity workflow imports successfully
- [ ] No import errors in logs
- [ ] Workflows available for entity processing

### Entity Processing ✅
- [ ] ExampleEntity creation succeeds
- [ ] Criteria validation executes and logs
- [ ] Processor executes and logs
- [ ] 3 OtherEntity instances created per ExampleEntity
- [ ] All gRPC events acknowledged

### Log Verification ✅
Look for these specific log patterns:
```
INFO:example_application.criterion.example_entity_validation_criterion.ExampleEntityValidationCriterion:Validating entity [entity-id]
INFO:example_application.criterion.example_entity_validation_criterion.ExampleEntityValidationCriterion:Entity [entity-id] passed all validation criteria
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:Processing ExampleEntity [entity-id]
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:Created OtherEntity [entity-id] (index 1)
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:Created OtherEntity [entity-id] (index 2)
INFO:example_application.processor.example_entity_processor.ExampleEntityProcessor:Created OtherEntity [entity-id] (index 3)
```

## 🚨 Common Issues and AI Solutions

### Issue: "Entity type not found"
**AI Command:**
```
"The entity discovery is failing. Please check the example_application/entity/__init__.py file and verify that entity classes are being discovered correctly. Also confirm ENTITY_NAME constants match workflow names exactly."
```

### Issue: "Processor not registered"
**AI Command:**
```
"The processor isn't being registered. Please check services/config.py and verify that 'example_application.processor' is in the modules list, then restart the application."
```

### Issue: "Workflow import fails"
**AI Command:**
```
"Workflow import is failing. Please verify that the entity_name parameter in the workflow import exactly matches the ENTITY_NAME constant in the entity class (PascalCase)."
```

### Issue: "Integration tests failing"
**AI Command:**
```
"Integration tests are failing. Please run the test suite with verbose output, identify the specific failures, and fix the underlying issues. Then re-run to confirm all 12 tests pass."
```

## 📊 Success Metrics

### Performance Benchmarks
- **Application startup**: < 10 seconds
- **Workflow import**: < 2 seconds per workflow
- **Entity processing**: < 5 seconds per entity
- **Integration tests**: < 30 seconds total

### Quality Standards
- **Test coverage**: > 80%
- **Code quality**: All tools pass (black, isort, mypy, flake8, bandit)
- **Integration tests**: 12/12 passing
- **E2E workflow**: Complete success with logging

## 🎯 AI Testing Best Practices

### 1. Be Specific
Instead of: "Test the application"
Use: "Run E2E test with ExampleEntity creation and verify processor creates 3 OtherEntity instances"

### 2. Request Verification
Always ask AI to:
- Show log output for verification
- Confirm specific success criteria
- Report any errors or warnings found

### 3. Incremental Testing
Test components in order:
1. Application startup
2. Workflow imports
3. Entity creation
4. Workflow execution
5. Integration tests

### 4. Error Handling
When issues occur:
- Ask AI to show full error messages
- Request specific troubleshooting steps
- Verify fixes with re-testing

## 📝 Reporting Results

### Success Report Template
```
✅ Cyoda E2E Test Results:
- Application: Started successfully
- Workflows: ExampleEntity and OtherEntity imported
- Entity Processing: [X] entities processed
- Processor: Created [X] OtherEntity instances
- Criteria: All validations passed
- Integration Tests: 12/12 passing
- Code Quality: All checks passed
```

### Issue Report Template
```
❌ Cyoda Test Issues Found:
- Issue: [Description]
- Component: [Affected component]
- Error: [Error message]
- Logs: [Relevant log entries]
- Fix Applied: [What was done]
- Verification: [How fix was confirmed]
```

Use these templates when communicating test results to the development team.
