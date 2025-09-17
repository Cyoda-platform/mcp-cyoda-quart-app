# Modern Python Package Management Guide

## Overview
This project now uses modern Python packaging standards with `pyproject.toml` as the single source of truth for all dependencies and tool configurations. We've eliminated `requirements.txt` in favor of the standardized approach.

## Project Structure
```
mcp-cyoda-quart-app/
├── pyproject.toml          # 📦 Single source of truth for everything
├── scripts/                # 🔧 Quality checking and utility scripts  
├── tests/                  # 🧪 Test files
└── src/                    # 📁 Source code (cyoda_mcp, common, etc.)
```

## Dependencies Management

### Runtime Dependencies
Located in `pyproject.toml` under `[project]` → `dependencies`:
```toml
dependencies = [
    "fastmcp>=2.12.0",
    "Quart>=0.19.9", 
    "grpcio>=1.64.1",
    # ... all runtime deps
]
```

### Development Dependencies  
Located in `pyproject.toml` under `[project.optional-dependencies]` → `dev`:
```toml
[project.optional-dependencies]
dev = [
    "pytest==7.4.0",
    "black==25.1.0",
    "isort==6.0.1", 
    "mypy==1.17.1",
    "flake8==7.1.6",
    "bandit==1.8.6",
    # ... all dev tools
]
```

## Installation Methods

### Method 1: Editable Install (Recommended for Development)
```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev]"

# This installs:
# - All runtime dependencies
# - All development tools (pytest, black, mypy, etc.)
# - The package itself in editable mode
```

### Method 2: Regular Install
```bash
# Install just the package and runtime dependencies
pip install .

# Install with dev dependencies
pip install ".[dev]"
```

### Method 3: From Git (for CI/CD or other projects)
```bash
# Install from git repository
pip install git+https://github.com/your-org/mcp-cyoda-quart-app.git

# With dev dependencies
pip install "git+https://github.com/your-org/mcp-cyoda-quart-app.git[dev]"
```

## Development Workflow

### 1. Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd mcp-cyoda-quart-app

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### 2. Daily Development
```bash
# Activate virtual environment
source .venv/bin/activate

# Your package is already installed and ready to use
# Any changes to source code are immediately available
```

### 3. Code Quality Checks
```bash
# Run all quality checks using the provided script
./scripts/quality_check.sh

# Or run individual tools:
python -m black .                    # Format code
python -m isort .                    # Sort imports  
python -m mypy .                     # Type checking
python -m flake8 .                   # Style checking
python -m bandit -r .                # Security scanning
python -m pytest --cov              # Run tests with coverage
```

### 4. Adding New Dependencies

#### Runtime Dependencies
```bash
# Add to pyproject.toml [project] dependencies array
# Then reinstall:
pip install -e .
```

#### Development Dependencies  
```bash
# Add to pyproject.toml [project.optional-dependencies] dev array
# Then reinstall:
pip install -e ".[dev]"
```

## Tool Configurations

All tools are configured in `pyproject.toml`:

### MyPy (Type Checking)
```toml
[tool.mypy]
python_version = "3.11"
strict = true
exclude = ["^proto/.*\\.py$", "^proto/.*\\.pyi$"]
# Proto files automatically excluded!
```

### Black (Code Formatting)
```toml
[tool.black]
line-length = 88
exclude = '''/(proto)/'''
```

### isort (Import Sorting)
```toml
[tool.isort]
profile = "black"
skip_glob = ["proto/*"]
```

### pytest (Testing)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --strict-markers"
```

### Coverage
```toml
[tool.coverage.run]
source = ["cyoda_mcp", "common", "entity", "service", "workflow", "routes"]
omit = ["proto/*", "*/tests/*"]
```

## Package Usage

### As a Library
```python
# After installation, import anywhere:
from cyoda_mcp import SomeClass
from common.service import EntityService
```

### As a Command Line Tool
```bash
# The package provides a CLI command:
mcp-cyoda --help

# This is defined in pyproject.toml:
# [project.scripts]
# mcp-cyoda = "cyoda_mcp.__main__:main"
```

## Building and Distribution

### Build Package
```bash
# Install build tools (included in dev dependencies)
pip install build

# Build wheel and source distribution
python -m build

# Output in dist/:
# - mcp_cyoda-0.1.2-py3-none-any.whl
# - mcp_cyoda-0.1.2.tar.gz
```

### Upload to PyPI (if applicable)
```bash
# Install twine (included in dev dependencies)  
pip install twine

# Upload to PyPI
python -m twine upload dist/*
```

## Benefits of This Approach

### ✅ **Standardized**
- Follows PEP 518, PEP 621, PEP 660 standards
- Single source of truth in `pyproject.toml`
- No more `requirements.txt`, `setup.py`, `setup.cfg` confusion

### ✅ **Tool Integration**
- All tools configured in one place
- Consistent exclusion patterns (proto files)
- No configuration drift between tools

### ✅ **Dependency Management**
- Clear separation of runtime vs development dependencies
- Version pinning where needed
- Optional dependency groups

### ✅ **Development Experience**
- Editable installs for immediate code changes
- Consistent environment setup
- Easy onboarding for new developers

### ✅ **CI/CD Friendly**
- Single command installation: `pip install -e ".[dev]"`
- Reproducible builds
- Clear dependency specifications

## Quick Start Commands

```bash
# 1. Setup development environment
pip install -e ".[dev]"

# 2. Run all quality checks
./scripts/quality_check.sh

# 3. Run individual tools
python -m mypy .                    # Type checking (proto files excluded!)
python -m black .                   # Code formatting
python -m isort .                   # Import sorting
python -m flake8 .                  # Style checking (venv & proto excluded!)
python -m bandit -r .               # Security scanning
python -m pytest --cov             # Tests with coverage

# 3a. Focused checks (recommended for development)
python -m flake8 cyoda_mcp/ common/ # Check only main source directories

# 4. Use the CLI tool
mcp-cyoda --help             # Show help
mcp-cyoda --version          # Show version
```

## Migration Complete! 🎉

- ❌ `requirements.txt` - **REMOVED** (replaced by pyproject.toml)
- ✅ `pyproject.toml` - **ENHANCED** (single source of truth)
- ✅ All tools configured and working with exact versions:
  - pytest==7.4.0, black==25.1.0, isort==6.0.1
  - mypy==1.17.1, flake8==7.1.1, bandit==1.8.6
- ✅ Proto files properly excluded from all tools
- ✅ Modern Python packaging standards followed
- ✅ CLI command `mcp-cyoda` available
- ✅ Type stubs installed for better mypy support

**Ready to develop!** Use `pip install -e ".[dev]"` and you're all set! 🚀
