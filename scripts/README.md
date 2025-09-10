# Scripts Directory

This directory contains utility scripts for the Cyoda MCP Client application.

## Available Scripts

### `import_workflows.py` - Workflow Import Tool

A standalone script that allows users to manually import workflows without using MCP tools.

#### Features
- Import workflows from JSON files
- Validate workflow files before import
- List available workflow files
- Support for both relative and absolute file paths
- Comprehensive error handling and validation

#### Usage Examples

```bash
# Import a specific workflow
python scripts/import_workflows.py --entity ExampleEntity --version 1 --file example_application/resources/workflow/exampleentity/version_1/ExampleEntity.json

# Import with custom mode
python scripts/import_workflows.py --entity MyEntity --version 2 --file path/to/workflow.json --mode MERGE

# List available workflow files
python scripts/import_workflows.py --list

# List workflow files in custom directory
python scripts/import_workflows.py --list --base-path custom/workflow/directory

# Validate a workflow file without importing
python scripts/import_workflows.py --entity ExampleEntity --version 1 --file path/to/workflow.json --validate-only
```

#### Command Line Options

- `--entity, -e`: Entity name (must match ENTITY_NAME in entity class)
- `--version, -v`: Model version (default: 1)
- `--file, -f`: Path to workflow JSON file (relative to project root or absolute)
- `--mode, -m`: Import mode (default: REPLACE)
- `--list, -l`: List available workflow files
- `--base-path, -b`: Base path for listing workflow files (default: application/resources/workflow)
- `--validate-only`: Only validate the workflow file without importing

#### Requirements

- The application must be properly configured with Cyoda credentials
- Workflow files must be valid JSON with proper structure
- Entity names must match exactly (case-sensitive) with the ENTITY_NAME in entity classes

#### Error Handling

The script provides comprehensive error handling for:
- File not found errors
- Invalid JSON format
- Missing required workflow fields
- Network connectivity issues
- Authentication failures

#### Output

The script provides clear success/failure messages with detailed information:
- ✅ Success: Shows entity name, version, file path, and number of workflows loaded
- ❌ Failure: Shows specific error messages and troubleshooting information

## Adding New Scripts

When adding new utility scripts to this directory:

1. **Follow the naming convention**: Use descriptive names with underscores
2. **Add proper documentation**: Include docstrings and help text
3. **Handle errors gracefully**: Provide clear error messages
4. **Use logging**: Configure appropriate logging levels
5. **Add to this README**: Document the new script's purpose and usage

## Script Development Guidelines

### Structure
```python
#!/usr/bin/env python3
"""
Script description and purpose
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description="Script description")
    # Add arguments
    args = parser.parse_args()
    
    # Script logic here
    
if __name__ == "__main__":
    asyncio.run(main())
```

### Best Practices
- Use async/await for I/O operations
- Provide comprehensive help text
- Validate inputs before processing
- Use type hints for better code quality
- Handle both relative and absolute paths
- Provide clear success/failure feedback

## Integration with Main Application

These scripts are designed to work with the main Cyoda MCP Client application:
- They use the same service layer (`services/services.py`)
- They follow the same configuration patterns
- They integrate with the same authentication system
- They use the same error handling patterns

This ensures consistency and reliability across all tools in the ecosystem.
