# Contributing to Cyoda Client Application

Welcome to the Cyoda Client Application project! This guide will help you understand how to contribute effectively to this codebase.

## 🏗️ Project Structure

### What Contributors Can Edit
Contributors are welcome to modify and improve all parts of the codebase **except** the `application/` directory:

```
├── common/                    ✅ Edit freely - Core utilities and shared code
├── services/                  ✅ Edit freely - Service layer and configuration  
├── tests/                     ✅ Edit freely - All test files
├── example_application/       ✅ Edit freely - Example code and templates
├── cyoda_mcp/                ✅ Edit freely - MCP tools and integrations
├── proto/                     ✅ Edit freely - Protocol buffer definitions
├── docs/                      ✅ Edit freely - Documentation
├── scripts/                   ✅ Edit freely - Build and utility scripts
├── application/               ❌ DO NOT EDIT - Reserved for end users
└── *.py, *.md, *.toml        ✅ Edit freely - Root configuration files
```

### Reserved Directory: `application/`
The `application/` directory is **reserved for end users** who will add their own business logic, entities, processors, and criteria. Contributors should:
- Use `example_application/` for examples and templates
- Test changes against `example_application/` 
- Never modify user code in `application/`

## 🛠️ Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd mcp-cyoda-quart-app

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Code Quality Standards

This project follows strict code quality standards. **Always run these checks before committing:**

```bash
# Format code
python -m black .

# Sort imports  
python -m isort .

# Type checking
python -m mypy .

# Style checking
python -m flake8 .

# Security scanning
python -m bandit -r .

# Run tests with coverage
python -m pytest --cov
```

#### Quality Requirements
- **Black**: Code must be formatted with Black
- **isort**: Imports must be sorted correctly
- **mypy**: No type checking errors allowed
- **flake8**: No style violations allowed
- **bandit**: No security issues allowed
- **pytest**: All tests must pass with good coverage

### 3. Testing Requirements

#### Integration Tests
All changes must pass the existing integration test suite:

```bash
python -m pytest tests/integration/test_grpc_handlers_e2e.py -v
```

**Expected Result**: 12/12 tests passing ✅

#### Adding New Tests
When adding new functionality:
- Add unit tests in `tests/unit/`
- Add integration tests in `tests/integration/`
- Ensure test coverage remains high
- Follow existing test patterns and naming conventions

## 🤖 Working with AI Assistance

### End-to-End Testing with AI
Contributors can ask AI assistants to run complete end-to-end tests. Here's how:

#### 1. Request E2E Testing
Ask the AI assistant:
```
"Please run end-to-end tests using the MCP tools to verify the complete workflow"
```

#### 2. Expected AI Actions
The AI should:
1. Start the application (`python run_app.py`)
2. Import workflows using MCP tools:
   ```python
   workflow_mgmt_import_workflows_from_file_tool_cyoda-mcp(
       entity_name="ExampleEntity",
       model_version="1",
       file_path="example_application/resources/workflow/exampleentity/version_1/ExampleEntity.json"
   )
   ```
3. Create test entities:
   ```python
   entity_create_entity_tool_cyoda-mcp(
       entity_model="exampleentity",
       entity_data={"name": "Test", "description": "E2E Test", "value": 100, "category": "ELECTRONICS", "isActive": true}
   )
   ```
4. Verify complete workflow execution in logs

#### 3. Success Criteria
The AI should confirm:
- ✅ Application starts without errors
- ✅ Processor and criteria are registered
- ✅ Workflows import successfully  
- ✅ Entity creation triggers complete workflow
- ✅ Criteria validation executes and logs
- ✅ Processor executes and creates 3 OtherEntity instances
- ✅ All gRPC communication completes successfully

### AI Testing Commands
Use these specific requests with AI assistants:

```bash
# Basic functionality test
"Run integration tests and verify they pass"

# Complete E2E workflow test  
"Import workflows and create test entities to verify end-to-end processing"

# Code quality check
"Run all code quality tools (black, isort, mypy, flake8, bandit) and fix any issues"

# Performance test
"Create multiple entities and verify processor handles them correctly"
```

## 📋 Contribution Checklist

Before submitting a pull request, ensure:

### Code Quality ✅
- [ ] Code formatted with `black`
- [ ] Imports sorted with `isort`
- [ ] No `mypy` type errors
- [ ] No `flake8` style violations
- [ ] No `bandit` security issues
- [ ] All tests pass with `pytest`

### Testing ✅  
- [ ] Integration tests pass (12/12)
- [ ] New functionality has tests
- [ ] E2E workflow verified with AI assistance
- [ ] No regressions in existing functionality

### Documentation ✅
- [ ] Code changes documented
- [ ] README updated if needed
- [ ] Examples updated in `example_application/`
- [ ] Breaking changes noted

### Architecture ✅
- [ ] No modifications to `application/` directory
- [ ] Changes follow existing patterns
- [ ] Proper separation of concerns maintained
- [ ] Backward compatibility preserved

## 🚀 Getting Help

### Resources
- **E2E Testing Guide**: See `CYODA_E2E_TESTING_GUIDE.md`
- **Package Management**: See `PACKAGE_MANAGEMENT_GUIDE.md`
- **Example Code**: Check `example_application/` directory

### AI Assistant Guidelines
When working with AI assistants:
1. Always specify you're working on the Cyoda client application
2. Mention you need E2E testing with MCP tools
3. Request verification of complete workflow execution
4. Ask for code quality checks before finalizing changes

### Common Issues
- **Import Errors**: Ensure you're using `example_application.*` imports, not `application.*`
- **Test Failures**: Run E2E tests with AI to identify workflow issues
- **Type Errors**: Use proper type hints and check with `mypy`
- **Entity Names**: Always use PascalCase for entity names (ExampleEntity, OtherEntity)

## 📝 Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Run** all code quality checks
4. **Test** with AI assistance for E2E verification
5. **Commit** changes (`git commit -m 'Add amazing feature'`)
6. **Push** to branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### PR Requirements
- Clear description of changes
- All quality checks passing
- Integration tests passing
- E2E workflow verified
- No breaking changes to user API

## 🔧 Development Tips

### Working with Entity Models
When modifying entity-related code:
- Entity names must be PascalCase: `ExampleEntity`, `OtherEntity`
- Use `ENTITY_NAME` class variable to define the exact name
- API calls use the exact entity name from `ENTITY_NAME`
- Workflow imports must match `ENTITY_NAME` exactly

### Processor and Criteria Development
- Processors go in `common/processor/` or `example_application/processor/`
- Criteria go in `common/criterion/` or `example_application/criterion/`
- Both must inherit from appropriate base classes
- Register in `services/config.py` modules list

### MCP Tools Usage
The project includes MCP (Model Context Protocol) tools for:
- `workflow_mgmt_*`: Import/export workflows
- `entity_*`: Create/read/update/delete entities
- `search_*`: Search and query entities

### Debugging Workflow Issues
1. Check application logs for gRPC events
2. Verify entity names match between model and workflow
3. Ensure workflows are imported before creating entities
4. Confirm processor/criteria are registered in logs

## 🧪 Testing Strategies

### Unit Testing
```bash
# Run specific test file
python -m pytest tests/unit/test_specific.py -v

# Run with coverage report
python -m pytest tests/unit/ --cov=common --cov-report=html
```

### Integration Testing
```bash
# Full integration test suite
python -m pytest tests/integration/ -v

# Specific handler tests
python -m pytest tests/integration/test_grpc_handlers_e2e.py::TestGrpcHandlersE2E::test_calc_handler_e2e -v
```

### Manual E2E Testing
1. Start application: `python run_app.py`
2. Import workflows via MCP tools
3. Create entities and observe logs
4. Verify processor creates related entities
5. Confirm criteria validation passes

## 🐛 Troubleshooting

### Common Error Patterns

#### "No module named 'application.entity'"
- **Cause**: Trying to import from user directory
- **Fix**: Use `example_application.entity` for development

#### "Entity type not found"
- **Cause**: Entity not registered or wrong name
- **Fix**: Check `ENTITY_NAME` matches workflow exactly

#### "Processor not found"
- **Cause**: Processor not registered in config
- **Fix**: Add to `services/config.py` modules list

#### "Workflow import failed"
- **Cause**: Entity name mismatch
- **Fix**: Use exact PascalCase name from entity model

### Getting Unstuck
1. **Check logs**: Application logs show detailed workflow execution
2. **Run E2E with AI**: Ask AI to run complete workflow test
3. **Verify examples**: Ensure `example_application/` works first
4. **Check imports**: Use correct module paths
5. **Ask for help**: Create issue with logs and error details

## 📚 Additional Resources

### Key Files to Understand
- `services/config.py`: Service configuration and module registration
- `common/processor/manager.py`: Processor discovery and execution
- `common/grpc_client/handlers/`: gRPC event handlers
- `example_application/`: Working examples of all components

### External Documentation
- **Cyoda Platform**: [Official Cyoda Documentation]
- **gRPC**: [gRPC Python Documentation]
- **Pydantic**: [Pydantic Documentation]
- **Quart**: [Quart Framework Documentation]

Thank you for contributing to the Cyoda Client Application! 🎉
