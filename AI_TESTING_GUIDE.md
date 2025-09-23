# AI Testing Guide for Cyoda Client Applications

This guide provides specific commands and prompts for working with AI assistants to test Cyoda Client Applications. It includes critical constraints, common issues, and step-by-step integration procedures discovered through extensive testing.

## 🚨 **CRITICAL CONSTRAINTS & REQUIREMENTS**

### **Entity Name Case Sensitivity** ⚠️
**MOST IMPORTANT**: Entity names for workflow import must **EXACTLY** match the `ENTITY_NAME` constant in your entity class:

Before starting the application, ensure you have imported all the workflows using the MCP tool workflow_mgmt_import_workflows_from_file_tool_cyoda-mcp.
DO NOT start the application before importing the workflows.
It is critical to import workflows before you start the application - otherwise the application will not work correctly
Retry until workflow import is successful.

```python
# In your entity class (e.g., application/entity/ your_entity/version_1/ your_entity.py)
class YourEntity(CyodaEntity):
    ENTITY_NAME: ClassVar[str] = "YourEntity"  # ← Use EXACTLY this for workflow import
    ENTITY_VERSION: ClassVar[int] = 1
```

```bash
# Workflow import - use EXACT case match
workflow_mgmt_import_workflows_from_file_tool_cyoda-mcp(
    entity_name="YourEntity",  # ← Must match ENTITY_NAME exactly
    model_version="1",
    file_path="application/resources/workflow/ your_entity/version_1/YourEntity.json"
)
```

**Common Mistakes:**
- ❌ Using `entity_name=" your_entity"` when `ENTITY_NAME = "YourEntity"`
- ❌ Using `entity_name="MAIL"` when `ENTITY_NAME = "YourEntity"`
- ✅ Using `entity_name="YourEntity"` when `ENTITY_NAME = "YourEntity"`

### **Directory Structure Requirements**
Your application must follow this structure:
```
application/                          # Your app directory (name may vary)
├── entity/
│   └── {entity_type}/               # e.g.,  your_entity, order, user
│       └── version_1/
│           └── {entity_class}.py    # e.g.,  your_entity.py, order.py
├── processor/
│   └── {entity}_processor.py       # e.g.,  your_entity_send_processor.py
├── criterion/
│   └── {entity}_criterion.py       # e.g.,  your_entity_validation_criterion.py
├── resources/
│   └── workflow/
│       └── {entity_type}/           # Must match entity directory name
│           └── version_1/
│               └── {EntityName}.json # e.g., YourEntity.json, Order.json
└── routes/
    └── {entity}.py                  # e.g.,  your_entity.py, order.py
```

## 🛠️ MCP Tools Setup

### Installing MCP Tools for AI Assistants

The Cyoda MCP Client provides tools that AI assistants can use directly. Install with:

```bash
# Install globally with pipx (recommended)
pipx install mcp-cyoda

# Or install with pip
pip install mcp-cyoda
```

### AI Assistant Configuration

Add this configuration to your AI assistant's MCP settings:

```json
{
  "mcpServers": {
    "cyoda": {
      "command": "mcp-cyoda",
      "env": {
        "CYODA_CLIENT_ID": "your-client-id-here",
        "CYODA_CLIENT_SECRET": "your-client-secret-here",
        "CYODA_HOST": "client-123.eu.cyoda.net"
      }
    }
  }
}
```

### Available MCP Tools

Once configured, AI assistants have access to these tools:

#### Entity Management Tools
- `entity_get_entity_tool_cyoda-mcp` - Retrieve entities by ID
- `entity_list_entities_tool_cyoda-mcp` - List all entities of a type
- `entity_create_entity_tool_cyoda-mcp` - Create new entities
- `entity_update_entity_tool_cyoda-mcp` - Update existing entities
- `entity_delete_entity_tool_cyoda-mcp` - Delete entities

#### Search Tools
- `search_find_all_cyoda-mcp` - Find all entities of a type
- `search_search_cyoda-mcp` - Advanced search with conditions

#### Workflow Management Tools
- `workflow_mgmt_export_workflows_to_file_tool_cyoda-mcp` - Export workflows
- `workflow_mgmt_import_workflows_from_file_tool_cyoda-mcp` - Import workflows
- `workflow_mgmt_list_workflow_files_tool_cyoda-mcp` - List workflow files
- `workflow_mgmt_validate_workflow_file_tool_cyoda-mcp` - Validate workflows

#### Edge Message Tools
- `edge_message_get_edge_message_tool_cyoda-mcp` - Retrieve messages
- `edge_message_send_edge_message_tool_cyoda-mcp` - Send messages

## 🔧 **WORKFLOW IMPORT TROUBLESHOOTING**

### **Issue: "Entity type not found" or "No workflow found"**
**Root Cause**: Entity name mismatch between class definition and workflow import.

**Solution**:
1. Check your entity class:
   ```python
   class YourEntity(CyodaEntity):
       ENTITY_NAME: ClassVar[str] = "YourEntity"  # ← Note the exact case
   ```

2. Use EXACT same name for workflow import:
   ```python
   workflow_mgmt_import_workflows_from_file_tool_cyoda-mcp(
       entity_name="YourEntity",  # ← Must match EXACTLY
       model_version="1",
       file_path="application/resources/workflow/yourentity/version_1/YourEntity.json"
   )
   ```

### **Issue: "Workflow import succeeds but no workflow execution"**
**Root Cause**: Workflow imported locally but not deployed to Cyoda environment.

**Solution**: Always verify workflow deployment by creating entities via routes API, not just MCP tools.

### **Issue: "Processor/Criteria not found"**
**Root Cause**: Processor/criteria not registered in services configuration.

**Solution**: Check `services/config.py`:
```python
"processor": {
    "modules": [
        "application.processor",     # ← Your app processors
        "application.criterion",     # ← Your app criteria
        # Add other modules as needed
    ],
},
```

## 🤖 AI Assistant Commands

### **Step-by-Step Integration Commands**

#### 1. **Discover Your Application Structure**
```
"Please examine the application directory structure and identify:
1. Entity classes and their ENTITY_NAME constants
2. Available processors and criteria
3. Workflow JSON files and their locations
4. Routes API endpoints
Show me the exact entity names and file paths I need for testing."
```

#### 2. **Import Workflows with Correct Entity Names**
```
"Import the workflow for [YourEntity] using MCP tools. Make sure to use the exact entity name from the ENTITY_NAME constant in the entity class. The workflow file is at application/resources/workflow/[entity_type]/version_1/[EntityName].json"
```

#### 3. **Test Complete E2E Workflow via Routes API**
```
"Start the application and test the complete workflow by:
1. Creating an entity via POST /api/[entity] routes API (not MCP tools)
2. Monitor application logs for criteria and processor execution
3. Verify the entity reaches final workflow state
4. Confirm all gRPC events are processed successfully"
```

#### 4. **Verify Integration Test Suite**
```
"Run the integration test suite (tests/integration/test_grpc_handlers_e2e.py) and confirm all tests pass. If any fail, analyze the failures and fix the underlying issues."
```

#### 5. **Code Quality Verification**
```
"Run all code quality tools on the application directory:
- black (formatting)
- isort (import sorting)
- mypy (type checking)
- flake8 (style checking)
- bandit (security scanning)
Fix any critical issues found."
```

## 📋 **DETAILED TESTING WORKFLOWS**

### **Template: Full E2E Workflow Test for Your Application**

**Step 1: Application Discovery and Setup**
```
"Please analyze my application directory and help me test the complete Cyoda workflow:

1. Examine the application/ directory structure
2. Identify entity classes and their ENTITY_NAME constants
3. Find workflow JSON files and their exact paths
4. Locate processor and criteria classes
5. Check routes API endpoints

Then start the application using: python -m application.app"
```

**Step 2: Workflow Import with Correct Entity Names**
```
"Import workflows for my entities using the exact entity names from the ENTITY_NAME constants. For each entity:

1. Use workflow_mgmt_import_workflows_from_file_tool_cyoda-mcp with:
   - entity_name: [EXACT ENTITY_NAME from class]
   - model_version: "1"
   - file_path: "application/resources/workflow/[entity_type]/version_1/[EntityName].json"

2. Verify import success before proceeding"
```

**Step 3: Test via Routes API (CRITICAL)**
```
"Test the workflow execution by creating entities via the routes API, NOT MCP tools:

1. Use curl or HTTP client to POST to /api/[entity_name]
2. Send proper JSON payload matching the entity fields
3. Monitor application logs for:
   - Criteria execution and results
   - Processor execution and completion
   - gRPC event processing
4. Verify entity reaches final workflow state
5. Check entity state via MCP tools to confirm completion"
```

**Expected Success Pattern:**
- ✅ Application starts with all processors/criteria registered
- ✅ Workflows import successfully with correct entity names
- ✅ Routes API creates entities successfully
- ✅ Logs show criteria validation execution
- ✅ Logs show processor execution and completion
- ✅ Entities reach final workflow states ("[*]")
- ✅ All gRPC communication completes successfully

### **Template: Code Quality Verification**

**Request:**
```
"Run comprehensive code quality checks on the application directory:

1. python -m black --check application/
2. python -m isort --check-only application/
3. python -m mypy application/ --no-error-summary
4. python -m flake8 --max-line-length=88 --extend-ignore=E203,W503 application/
5. python -m bandit -r application/ -f json
6. python -m pytest tests/integration/ -v

Report results and fix any critical issues found."
```

**Expected Results:**
- ✅ Black: All files formatted correctly
- ✅ isort: Import sorting correct
- ✅ MyPy: No type errors
- ⚠️ Flake8: May have line length warnings (acceptable)
- ✅ Bandit: No security issues
- ✅ Integration tests: All tests pass

### **Template: MCP Tools Functionality Testing**

**Request:**
```
"Test all MCP tools functionality with my application:

1. List available workflow files:
   workflow_mgmt_list_workflow_files_tool_cyoda-mcp(base_path="application/resources/workflow")

2. Validate workflow files for each entity:
   workflow_mgmt_validate_workflow_file_tool_cyoda-mcp(file_path="application/resources/workflow/[entity_type]/version_1/[EntityName].json")

3. Test entity search with conditions:
   search_search_cyoda-mcp(
       entity_model="[your_entity_model]",
       search_conditions={"type": "simple", "jsonPath": "$.[field_name]", "operatorType": "EQUALS", "value": "[test_value]"}
   )

4. Test entity retrieval:
   entity_get_entity_tool_cyoda-mcp(
       entity_model="[your_entity_model]",
       entity_id="[entity_id_from_previous_test]"
   )

5. List all entities:
   entity_list_entities_tool_cyoda-mcp(entity_model="[your_entity_model]")

Verify all tools work correctly and return expected results."
```

**Expected Results:**
- ✅ Workflow files listed correctly from application directory
- ✅ Workflow validation passes for all entity workflows
- ✅ Search returns filtered results based on entity fields
- ✅ Entity retrieval works with proper entity IDs
- ✅ Entity listing shows all created entities
- ✅ No tool execution errors

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

## 🚨 **COMMON ISSUES AND SOLUTIONS**

### **Issue: "Entity type not found" or "No workflow found"**
**Root Cause**: Entity name case mismatch between class and workflow import.

**AI Command:**
```
"I'm getting 'Entity type not found' errors. Please:
1. Check my entity class ENTITY_NAME constant: find the exact case used
2. Verify I'm using the EXACT same case in workflow import
3. Show me the correct workflow import command with proper entity_name
4. Confirm the workflow file path matches the entity directory structure"
```

### **Issue: "Workflow import succeeds but entities don't execute workflow"**
**Root Cause**: Workflow imported locally but not deployed to Cyoda environment.

**AI Command:**
```
"My workflow import reports success but entities created via MCP tools don't execute the workflow. Please:
1. Test workflow execution by creating entities via routes API instead of MCP tools
2. Use curl POST /api/[entity] with proper JSON payload
3. Monitor application logs for criteria and processor execution
4. Verify entities reach final workflow states"
```

### **Issue: "Processor/Criteria not registered"**
**Root Cause**: Modules not included in services configuration.

**AI Command:**
```
"My processors/criteria aren't being registered. Please check services/config.py and verify that 'application.processor' and 'application.criterion' are in the modules list. Show me the correct configuration and restart the application."
```

### **Issue: "Routes API returns 404 or 500 errors"**
**Root Cause**: Blueprint not registered or entity service issues.

**AI Command:**
```
"My routes API isn't working. Please:
1. Check that the blueprint is registered in application/app.py
2. Verify the route definitions in application/routes/[entity].py
3. Confirm entity service is properly configured
4. Test with a simple GET request first"
```

### **Issue: "Integration tests failing"**
**Root Cause**: Various application configuration issues.

**AI Command:**
```
"Integration tests are failing. Please:
1. Run pytest tests/integration/ -v to see detailed failures
2. Check if processors and criteria are registered correctly
3. Verify gRPC connection is established
4. Fix any configuration issues and re-run tests"
```

### **Issue: "MCP tools not responding"**
**Root Cause**: MCP server configuration or authentication issues.

**AI Command:**
```
"MCP tools aren't working. Please verify:
1. mcp-cyoda package is installed correctly
2. Environment variables are set: CYODA_CLIENT_ID, CYODA_CLIENT_SECRET, CYODA_HOST
3. MCP server configuration is correct in AI assistant settings
4. Test basic functionality with entity_list_entities_tool_cyoda-mcp"
```

### **Issue: "Workflow validation fails"**
**Root Cause**: Invalid JSON structure or missing required fields.

**AI Command:**
```
"My workflow file validation is failing. Please:
1. Use workflow_mgmt_validate_workflow_file_tool_cyoda-mcp to check the file
2. Verify JSON syntax is correct
3. Check that processor and criteria names match registered classes
4. Ensure all required workflow fields are present"
```

## 📊 **SUCCESS METRICS & BENCHMARKS**

### **Performance Benchmarks**
- **Application startup**: < 10 seconds
- **Workflow import**: < 2 seconds per workflow
- **Entity creation via routes API**: < 1 second per entity
- **Workflow execution (criteria + processor)**: < 5 seconds per entity
- **Integration tests**: < 30 seconds total
- **End-to-end workflow**: < 10 seconds from creation to completion

### **Quality Standards**
- **MyPy**: No type errors (critical)
- **Bandit**: No security issues (critical)
- **Black**: Code formatting correct (critical)
- **isort**: Import sorting correct (critical)
- **Flake8**: Style violations acceptable if minor (line length warnings OK)
- **Integration tests**: All tests passing (critical)
- **E2E workflow**: Complete success with proper logging

### **Workflow Execution Success Criteria**
- ✅ **Application Startup**: All processors and criteria registered
- ✅ **Workflow Import**: Success with correct entity names
- ✅ **Entity Creation**: Via routes API (not just MCP tools)
- ✅ **Criteria Execution**: Logged with results
- ✅ **Processor Execution**: Logged with completion status
- ✅ **State Progression**: Entities reach final states ("[*]")
- ✅ **gRPC Communication**: All events acknowledged

## 🎯 **AI TESTING BEST PRACTICES**

### **1. Be Specific with Entity Names**
❌ **Avoid**: "Test the application with entities"
✅ **Use**: "Test workflow execution with [YourEntity] using exact ENTITY_NAME from the class definition"

### **2. Always Test via Routes API**
❌ **Avoid**: "Create entities using MCP tools only"
✅ **Use**: "Create entities via POST /api/[entity] routes API to ensure proper workflow execution"

### **3. Request Comprehensive Verification**
Always ask AI to:
- Show complete application logs for criteria and processor execution
- Verify entities reach final workflow states ("[*]")
- Confirm gRPC events are processed and acknowledged
- Check entity states via MCP tools after creation

### **4. Follow Incremental Testing Order**
Test components in this specific order:
1. **Application startup** - Verify processors/criteria registration
2. **Workflow import** - Use exact entity names from ENTITY_NAME constants
3. **Routes API testing** - Create entities via HTTP endpoints
4. **Workflow execution** - Monitor logs for criteria/processor execution
5. **State verification** - Confirm entities reach final states
6. **Integration tests** - Run full test suite

### **5. Comprehensive Error Handling**
When issues occur:
- Ask AI to show complete error messages and stack traces
- Request specific troubleshooting steps based on error type
- Verify fixes by re-running the complete workflow test
- Always test both success and failure scenarios

## 📝 **EXAMPLE AI CONVERSATION TEMPLATE**

**User:** "Please test my Cyoda application end-to-end using the application directory"

**AI Response:** "I'll run a complete E2E test of your Cyoda client application:

**1. Application Discovery:**
✅ Found entity: YourEntity with ENTITY_NAME = "YourEntity"
✅ Located workflow: application/resources/workflow/ your_entity/version_1/YourEntity.json
✅ Found processors: YourEntityProcessor
✅ Found criteria: YourEntityCriterion

**2. Application Startup:**
✅ Application started successfully
✅ Processors registered: YourEntityProcessor
✅ Criteria registered: YourEntityIsHappyCriterion, YourEntityCriterion
✅ gRPC connection established

**3. Workflow Import (Critical - Using Exact Entity Name):**
✅ YourEntity workflow imported using entity_name="YourEntity" (matching ENTITY_NAME constant)
✅ Workflow deployment successful

**4. Routes API Testing:**
✅ Happy YourEntity created via POST /api/ your_entity: ID 2d1c56ec-3adf-11b2-b83e-e6f027731b46
✅ Gloomy YourEntity created via POST /api/ your_entity: ID 3c74b7d8-3adf-11b2-b83e-e6f027731b46

**5. Workflow Execution Verification:**
✅ Happy YourEntity: YourEntityIsHappyCriterion → True → YourEntityProcessor → Success
✅ Gloomy YourEntity: YourEntityIsHappyCriterion → False → YourEntityCriterion → True →   → Success
✅ Both entities reached final state "[*]"

**6. Integration Tests:**
✅ All 12 integration tests passed

**Test Summary: Complete Success ✅**
- ✅ Workflow deployment: Working with correct entity names
- ✅ Routes API: Working for entity creation
- ✅ Workflow execution: Both happy and gloomy paths working
- ✅ State management: Proper progression to final states
- ✅ Integration tests: All passing"

## 📊 **REPORTING RESULTS**

### **Success Report Template**
```
✅ Cyoda E2E Test Results - [Your Application]:
- Application: Started successfully with all processors/criteria registered
- Workflow Import: [EntityName] workflow imported with correct entity_name
- Routes API: Entity creation via POST /api/[entity] working
- Workflow Execution: [X] entities processed with complete workflow execution
- Criteria: All validations executed and logged
- Processors: All processors executed successfully and logged
- State Management: Entities reached final states ("[*]")
- gRPC Communication: All events processed and acknowledged
- Integration Tests: [X]/[X] passing
- Code Quality: MyPy, Bandit, Black, isort passing
```

### **Issue Report Template**
```
❌ Cyoda Test Issues Found:
- Issue: [Description]
- Root Cause: [Entity name mismatch/Configuration issue/etc.]
- Component: [Workflow import/Routes API/Processor/etc.]
- Error: [Complete error message]
- Logs: [Relevant log entries]
- Fix Applied: [Specific solution implemented]
- Verification: [How fix was confirmed - re-run test results]
```

Use these templates when communicating test results. Always include specific entity names, file paths, and verification steps for your application.

---

## 🎯 **QUICK REFERENCE CHECKLIST**

### **Pre-Testing Setup**
- [ ] MCP tools installed and configured
- [ ] Environment variables set (CYODA_CLIENT_ID, CYODA_CLIENT_SECRET, CYODA_HOST)
- [ ] Application directory structure verified
- [ ] Entity classes have ENTITY_NAME constants defined

### **Critical Testing Steps**
- [ ] **Entity Name Verification**: Use EXACT case from ENTITY_NAME constant
- [ ] **Workflow Import**: Import using correct entity_name parameter
- [ ] **Routes API Testing**: Create entities via POST /api/[entity] (not MCP tools)
- [ ] **Log Monitoring**: Watch for criteria and processor execution
- [ ] **State Verification**: Confirm entities reach final states ("[*]")
- [ ] **Integration Tests**: Run and verify all tests pass

### **Success Indicators**
- [ ] Application starts with all processors/criteria registered
- [ ] Workflow import succeeds with correct entity names
- [ ] Routes API creates entities successfully
- [ ] Application logs show criteria execution and results
- [ ] Application logs show processor execution and completion
- [ ] Entities progress through workflow states to completion
- [ ] All gRPC events are processed and acknowledged
- [ ] Integration test suite passes completely

### **Common Pitfalls to Avoid**
- [ ] ❌ Using lowercase entity names when class uses PascalCase
- [ ] ❌ Testing only with MCP tools instead of routes API
- [ ] ❌ Ignoring application logs during workflow execution
- [ ] ❌ Not verifying final entity states
- [ ] ❌ Skipping integration test verification

**Remember**: The most critical factor is using the EXACT entity name from your ENTITY_NAME constant when importing workflows. This single issue causes most integration failures.
