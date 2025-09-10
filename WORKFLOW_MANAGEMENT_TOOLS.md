# Enhanced Workflow Management Tools 🔄

The MCP workflow management tools have been enhanced with file-based import/export functionality, making workflow management much more flexible and developer-friendly.

## 🆕 New Tools Added

### 1. `workflow_mgmt_export_workflows_to_file_tool`
Export entity workflows directly to JSON files with configurable paths.

**Parameters:**
- `entity_name`: Name of the entity (e.g., "ExampleEntity")
- `model_version`: Version of the model (e.g., "1")
- `file_path`: Path where to save the workflow file (relative to project root or absolute)

**Example Usage:**
```bash
# Export ExampleEntity workflows to a file
workflow_mgmt_export_workflows_to_file_tool(
    entity_name="ExampleEntity",
    model_version="1", 
    file_path="exported_workflows/ExampleEntity_v1.json"
)
```

### 2. `workflow_mgmt_import_workflows_from_file_tool`
Import entity workflows from JSON files with validation.

**Parameters:**
- `entity_name`: Name of the entity
- `model_version`: Version of the model
- `file_path`: Path to the workflow file (relative to project root or absolute)
- `import_mode`: Import mode ("REPLACE" or other supported modes)

**Example Usage:**
```bash
# Import workflows from a file
workflow_mgmt_import_workflows_from_file_tool(
    entity_name="ExampleEntity",
    model_version="1",
    file_path="exported_workflows/ExampleEntity_v1.json",
    import_mode="REPLACE"
)
```

### 3. `workflow_mgmt_list_workflow_files_tool`
List all available workflow files in a directory with metadata.

**Parameters:**
- `base_path`: Base directory to search (default: "resources/workflow")

**Example Usage:**
```bash
# List all workflow files
workflow_mgmt_list_workflow_files_tool(base_path="resources/workflow")
```

**Sample Output:**
```json
{
  "success": true,
  "base_path": "/path/to/project/resources/workflow",
  "files_count": 2,
  "workflow_files": [
    {
      "file_path": "/path/to/project/resources/workflow/exampleentity/version_1/ExampleEntity.json",
      "relative_path": "exampleentity/version_1/ExampleEntity.json",
      "file_name": "ExampleEntity.json",
      "size_bytes": 1234,
      "entity_name": "exampleentity",
      "model_version": "1",
      "workflows_count": 1,
      "workflow_name": "ExampleEntity Workflow",
      "workflow_version": "1.0"
    }
  ]
}
```

### 4. `workflow_mgmt_validate_workflow_file_tool`
Validate workflow files for correct JSON structure and required fields.

**Parameters:**
- `file_path`: Path to the workflow file to validate

**Example Usage:**
```bash
# Validate a workflow file
workflow_mgmt_validate_workflow_file_tool(
    file_path="resources/workflow/exampleentity/version_1/ExampleEntity.json"
)
```

**Sample Output:**
```json
{
  "success": true,
  "file_path": "/path/to/workflow/file.json",
  "file_size": 1234,
  "workflows_count": 1,
  "structure": "single_object",
  "is_valid": true,
  "warnings": [],
  "errors": []
}
```

## 🔧 Enhanced Existing Tools

### `workflow_mgmt_copy_workflows_between_entities_tool`
Copy workflows from one entity to another (unchanged but now works with file-based workflows).

## 📁 File Path Handling

### Relative Paths
All tools support relative paths that are resolved relative to the project root:
```bash
file_path="resources/workflow/MyEntity_v1.json"  # Relative to project root
file_path="exported_workflows/backup.json"       # Relative to project root
```

### Absolute Paths
Absolute paths are also supported:
```bash
file_path="/home/user/workflows/MyEntity.json"   # Absolute path
```

### Automatic Directory Creation
The export tool automatically creates directories if they don't exist:
```bash
file_path="new_directory/subdirectory/workflow.json"  # Creates directories as needed
```

## 🎯 Common Use Cases

### 1. Backup Workflows
```bash
# Export current workflows to backup
workflow_mgmt_export_workflows_to_file_tool(
    entity_name="ExampleEntity",
    model_version="1",
    file_path="backups/ExampleEntity_backup_$(date +%Y%m%d).json"
)
```

### 2. Environment Migration
```bash
# Export from source environment
workflow_mgmt_export_workflows_to_file_tool(
    entity_name="ExampleEntity",
    model_version="1",
    file_path="migration/ExampleEntity_prod.json"
)

# Import to target environment
workflow_mgmt_import_workflows_from_file_tool(
    entity_name="ExampleEntity",
    model_version="1",
    file_path="migration/ExampleEntity_prod.json"
)
```

### 3. Version Control Integration
```bash
# Export workflows to version-controlled directory
workflow_mgmt_export_workflows_to_file_tool(
    entity_name="ExampleEntity",
    model_version="1",
    file_path="resources/workflow/exampleentity/version_1/ExampleEntity.json"
)
```

### 4. Workflow Development & Testing
```bash
# List available workflow files
workflow_mgmt_list_workflow_files_tool()

# Validate before importing
workflow_mgmt_validate_workflow_file_tool(
    file_path="development/new_workflow.json"
)

# Import validated workflow
workflow_mgmt_import_workflows_from_file_tool(
    entity_name="TestEntity",
    model_version="1",
    file_path="development/new_workflow.json"
)
```

## 🛡️ Error Handling

All tools provide comprehensive error handling:
- File not found errors
- JSON parsing errors
- Validation errors
- Permission errors
- Service connectivity errors

## 📊 Current Project Structure

```
resources/
└── workflow/
    ├── exampleentity/
    │   └── version_1/
    │       └── ExampleEntity.json
    └── otherentity/
        └── version_1/
            └── OtherEntity.json

exported_workflows/
└── ExampleEntity_v1.json  # Example exported workflow
```

## 🚀 Benefits

1. **File-based workflow management** - Easy to version control and backup
2. **Flexible path handling** - Support for both relative and absolute paths
3. **Automatic validation** - Ensure workflow integrity before import
4. **Comprehensive metadata** - Rich information about workflow files
5. **Developer-friendly** - Integrates seamlessly with existing development workflows
6. **Error resilience** - Robust error handling and reporting

These enhanced tools make workflow management much more powerful and developer-friendly! 🎉
