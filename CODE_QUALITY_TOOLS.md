# Code Quality Tools for Cyoda Client Application

This document describes the tools available for checking compilation errors, code smells, and overall code quality in the Cyoda client application.

## Quick Start

### 1. Run All Checks (Recommended)
```bash
./scripts/check_code.sh
```

### 2. Run Comprehensive Python Analysis
```bash
python scripts/code_quality_check.py
```

### 3. Run Specific Tests
```bash
# Run only the integration tests
python -m pytest tests/integration/test_grpc_handlers_e2e.py -v

# Run specific test
python -m pytest tests/integration/test_grpc_handlers_e2e.py::TestGrpcHandlersE2E::test_calc_handler_e2e -v
```

## Available Tools

### 1. Syntax and Compilation Checks

#### Python Syntax Check
```bash
# Check all Python files for syntax errors
python scripts/code_quality_check.py --check syntax

# Manual check for specific file
python -m py_compile path/to/file.py
```

#### Import Structure Check
```bash
# Check for import issues and circular dependencies
python scripts/code_quality_check.py --check imports
```

### 2. Code Style and Quality

#### Flake8 (Style and Error Detection)
```bash
# Install flake8
pip install flake8

# Run style check
flake8 --max-line-length=120 --ignore=E203,W503,E501 --exclude=.venv,__pycache__,.pytest_cache .

# Or use the wrapper
python scripts/code_quality_check.py --check flake8
```

#### Black (Code Formatting)
```bash
# Install black
pip install black

# Format code
black --line-length=120 .

# Check what would be formatted
black --check --line-length=120 .
```

#### isort (Import Sorting)
```bash
# Install isort
pip install isort

# Sort imports
isort .

# Check import order
isort --check-only .
```

### 3. Type Checking

#### MyPy (Static Type Analysis)
```bash
# Install mypy
pip install mypy

# Run type checking
mypy --ignore-missing-imports --no-strict-optional --show-error-codes .

# Or use the wrapper
python scripts/code_quality_check.py --check mypy
```

### 4. Security Analysis

#### Bandit (Security Vulnerability Scanner)
```bash
# Install bandit
pip install bandit

# Run security scan
bandit -r . --exclude .venv,__pycache__,.pytest_cache

# Get JSON output
bandit -r . -f json --exclude .venv

# Or use the wrapper
python scripts/code_quality_check.py --check bandit
```

### 5. Testing

#### Pytest (Test Execution)
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/integration/test_grpc_handlers_e2e.py -v

# Run with coverage
pip install pytest-cov
python -m pytest --cov=. --cov-report=html

# Or use the wrapper
python scripts/code_quality_check.py --check pytest
```

### 6. Advanced Analysis

#### Pylint (Comprehensive Code Analysis)
```bash
# Install pylint
pip install pylint

# Run pylint on specific module
pylint workflow/processors/example_entity_processor.py

# Run on entire project
pylint --recursive=y .
```

#### Complexity Analysis
```bash
# Install radon for complexity metrics
pip install radon

# Cyclomatic complexity
radon cc . -a

# Maintainability index
radon mi .

# Raw metrics
radon raw .
```

## Integration Test Coverage

The integration test suite (`tests/integration/test_grpc_handlers_e2e.py`) provides comprehensive end-to-end testing:

### Test Categories

1. **Entity Creation Tests**
   - Dynamic entity creation
   - Entity factory functionality
   - Type validation

2. **gRPC Handler Tests**
   - CalcRequestHandler end-to-end flow
   - CriteriaCalcRequestHandler validation
   - Response format verification
   - Error handling scenarios

3. **Processor Integration Tests**
   - ExampleEntityProcessor functionality
   - Entity processing with mocked services
   - Business logic validation

4. **Criteria Validation Tests**
   - ExampleEntityValidationCriterion testing
   - Business rule validation
   - Edge cases and boundary conditions

5. **Workflow Integration Tests**
   - Complete validation → processing workflow
   - Concurrent processing capabilities
   - Error recovery and handling

6. **Performance and Concurrency Tests**
   - Concurrent entity processing
   - Load testing with multiple entities
   - Resource management validation

### Running Specific Test Categories

```bash
# Run all integration tests
python -m pytest tests/integration/ -v

# Run specific test categories
python -m pytest tests/integration/test_grpc_handlers_e2e.py::TestGrpcHandlersE2E::test_calc_handler_e2e -v
python -m pytest tests/integration/test_grpc_handlers_e2e.py::TestGrpcHandlersE2E::test_criteria_calc_handler_e2e -v
python -m pytest tests/integration/test_grpc_handlers_e2e.py::TestGrpcHandlersE2E::test_concurrent_processing -v

# Run with detailed output
python -m pytest tests/integration/ -v -s --tb=long

# Run with coverage
python -m pytest tests/integration/ --cov=workflow --cov=common --cov=entity --cov-report=html
```

## Continuous Integration Setup

For CI/CD pipelines, create a `.github/workflows/quality.yml` or similar:

```yaml
name: Code Quality
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install flake8 mypy bandit pytest-cov
      - name: Run quality checks
        run: python scripts/code_quality_check.py --json
      - name: Run tests
        run: python -m pytest tests/ --cov=. --cov-report=xml
```

## Common Issues and Solutions

### 1. Import Errors
- **Issue**: `ModuleNotFoundError` during testing
- **Solution**: Ensure `PYTHONPATH` includes project root or use `python -m pytest`

### 2. Service Initialization Errors
- **Issue**: `Services not initialized` in processors
- **Solution**: Mock services properly in tests or call `initialize_services()`

### 3. Pydantic Deprecation Warnings
- **Issue**: Pydantic v1 style validators deprecated
- **Solution**: Migrate to `@field_validator` (v2 style) or suppress warnings

### 4. Async Test Issues
- **Issue**: `RuntimeError: no running event loop`
- **Solution**: Use `@pytest.mark.asyncio` and ensure proper async/await usage

## Output Formats

### JSON Output
```bash
# Get machine-readable results
python scripts/code_quality_check.py --json > quality_report.json
```

### HTML Reports
```bash
# Generate HTML coverage report
python -m pytest --cov=. --cov-report=html
# View at htmlcov/index.html

# Generate HTML complexity report
radon cc . -a --json | python -m json.tool > complexity.json
```

This comprehensive toolset ensures high code quality and helps maintain the Cyoda client application's reliability and maintainability.
