"""
Workflow Management MCP Presentation Layer

This module provides FastMCP tools for workflow management operations,
including file-based import/export functionality.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import Context, FastMCP

from services.services import get_workflow_management_service

# Add the parent directory to the path so we can import from the main app
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Create the MCP server for workflow management operations
mcp = FastMCP("Workflow Management")


@mcp.tool
async def export_workflows_to_file_tool(
    entity_name: str,
    model_version: str,
    file_path: str,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Export entity workflows to a JSON file.

    Args:
        entity_name: Name of the entity
        model_version: Version of the model
        file_path: Path where to save the workflow file (relative to project root or absolute)
        ctx: FastMCP context for logging

    Returns:
        Dictionary containing export result or error information
    """
    try:
        if ctx:
            await ctx.info(
                f"Exporting workflows for entity {entity_name} version {model_version} to {file_path}"
            )

        # Get workflows from Cyoda
        workflow_management_service = get_workflow_management_service()
        export_result = await workflow_management_service.export_entity_workflows(
            entity_name=entity_name, model_version=model_version
        )

        if not export_result.get("success", False):
            return export_result

        workflows = export_result.get("workflows", [])
        if not workflows:
            return {
                "success": False,
                "error": f"No workflows found for entity {entity_name} version {model_version}",
                "entity_name": entity_name,
                "model_version": model_version,
            }

        # Resolve file path (relative to project root if not absolute)
        if not os.path.isabs(file_path):
            # Get project root (3 levels up from this file)
            project_root = Path(__file__).parent.parent.parent
            full_path = project_root / file_path
        else:
            full_path = Path(file_path)

        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write workflows to file
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(workflows, f, indent=2, ensure_ascii=False)

        if ctx:
            await ctx.info(
                f"Successfully exported {len(workflows)} workflows to {full_path}"
            )

        return {
            "success": True,
            "message": f"Exported {len(workflows)} workflows to {full_path}",
            "file_path": str(full_path),
            "workflows_count": len(workflows),
            "entity_name": entity_name,
            "model_version": model_version,
        }

    except Exception as e:
        error_msg = f"Failed to export workflows to file: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "entity_name": entity_name,
            "model_version": model_version,
            "file_path": file_path,
        }


@mcp.tool
async def import_workflows_from_file_tool(
    entity_name: str,
    model_version: str,
    file_path: str,
    import_mode: str = "REPLACE",
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Import entity workflows from a JSON file.

    Args:
        entity_name: Name of the entity
        model_version: Version of the model
        file_path: Path to the workflow file (relative to project root or absolute)
        import_mode: Import mode ("REPLACE" or other supported modes)
        ctx: FastMCP context for logging

    Returns:
        Dictionary containing import result or error information
    """
    try:
        if ctx:
            await ctx.info(
                f"Importing workflows for entity {entity_name} version {model_version} from {file_path}"
            )

        # Resolve file path (relative to project root if not absolute)
        if not os.path.isabs(file_path):
            # Get project root (3 levels up from this file)
            project_root = Path(__file__).parent.parent.parent
            full_path = project_root / file_path
        else:
            full_path = Path(file_path)

        # Check if file exists
        if not full_path.exists():
            return {
                "success": False,
                "error": f"Workflow file not found: {full_path}",
                "entity_name": entity_name,
                "model_version": model_version,
                "file_path": file_path,
            }

        # Read workflows from file
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                workflow = json.load(f)
                workflows = workflow if isinstance(workflow, list) else [workflow]
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in workflow file: {str(e)}",
                "entity_name": entity_name,
                "model_version": model_version,
                "file_path": str(full_path),
            }

        # Validate workflows is a list
        if not isinstance(workflows, list):
            return {
                "success": False,
                "error": "Workflow file must contain a JSON array of workflow definitions",
                "entity_name": entity_name,
                "model_version": model_version,
                "file_path": str(full_path),
            }

        if ctx:
            await ctx.info(f"Loaded {len(workflows)} workflows from {full_path}")

        # Import workflows to Cyoda
        workflow_management_service = get_workflow_management_service()
        import_result = await workflow_management_service.import_entity_workflows(
            entity_name=entity_name,
            model_version=model_version,
            workflows=workflows,
            import_mode=import_mode,
        )

        # Enhance result with file information
        if import_result.get("success", False):
            import_result["file_path"] = str(full_path)
            import_result["workflows_loaded"] = len(workflows)
            if ctx:
                await ctx.info(
                    f"Successfully imported {len(workflows)} workflows from {full_path}"
                )

        return import_result

    except Exception as e:
        error_msg = f"Failed to import workflows from file: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "entity_name": entity_name,
            "model_version": model_version,
            "file_path": file_path,
        }


@mcp.tool
async def list_workflow_files_tool(
    base_path: str = "application/resources/workflow",
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    List available workflow files in the specified directory.

    Args:
        base_path: Base directory to search for workflow files (relative to project root or absolute)
        ctx: FastMCP context for logging

    Returns:
        Dictionary containing list of workflow files or error information
    """
    try:
        if ctx:
            await ctx.info(f"Listing workflow files in {base_path}")

        # Resolve base path (relative to project root if not absolute)
        if not os.path.isabs(base_path):
            # Get project root (3 levels up from this file)
            project_root = Path(__file__).parent.parent.parent
            full_base_path = project_root / base_path
        else:
            full_base_path = Path(base_path)

        if not full_base_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {full_base_path}",
                "base_path": base_path,
            }

        # Find all JSON files recursively
        workflow_files = []
        for json_file in full_base_path.rglob("*.json"):
            relative_path = json_file.relative_to(full_base_path)

            # Try to extract entity info from path structure
            path_parts = relative_path.parts
            entity_info = {
                "file_path": str(json_file),
                "relative_path": str(relative_path),
                "file_name": json_file.name,
                "size_bytes": json_file.stat().st_size,
            }

            # Try to parse entity name and version from directory structure
            if len(path_parts) >= 2:
                entity_info["entity_name"] = path_parts[0]
                if path_parts[1].startswith("version_"):
                    entity_info["model_version"] = path_parts[1].replace("version_", "")

            # Try to read basic workflow info
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
                    if isinstance(workflow_data, list) and workflow_data:
                        entity_info["workflows_count"] = len(workflow_data)
                        # Get info from first workflow if available
                        first_workflow = workflow_data[0]
                        if isinstance(first_workflow, dict):
                            entity_info["workflow_name"] = first_workflow.get("name")
                            entity_info["workflow_version"] = first_workflow.get(
                                "version"
                            )
                    elif isinstance(workflow_data, dict):
                        entity_info["workflows_count"] = 1
                        entity_info["workflow_name"] = workflow_data.get("name")
                        entity_info["workflow_version"] = workflow_data.get("version")
            except (json.JSONDecodeError, IOError):
                entity_info["error"] = "Could not read workflow file"

            workflow_files.append(entity_info)

        # Sort by entity name and version
        workflow_files.sort(
            key=lambda x: (
                x.get("entity_name", ""),
                x.get("model_version", ""),
                x.get("file_name", ""),
            )
        )

        if ctx:
            await ctx.info(f"Found {len(workflow_files)} workflow files")

        return {
            "success": True,
            "base_path": str(full_base_path),
            "files_count": len(workflow_files),
            "workflow_files": workflow_files,
        }

    except Exception as e:
        error_msg = f"Failed to list workflow files: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "base_path": base_path,
        }


@mcp.tool
async def validate_workflow_file_tool(
    file_path: str,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """
    Validate a workflow file for correct JSON structure and required fields.

    Args:
        file_path: Path to the workflow file (relative to project root or absolute)
        ctx: FastMCP context for logging

    Returns:
        Dictionary containing validation result or error information
    """
    try:
        if ctx:
            await ctx.info(f"Validating workflow file: {file_path}")

        # Resolve file path (relative to project root if not absolute)
        if not os.path.isabs(file_path):
            # Get project root (3 levels up from this file)
            project_root = Path(__file__).parent.parent.parent
            full_path = project_root / file_path
        else:
            full_path = Path(file_path)

        # Check if file exists
        if not full_path.exists():
            return {
                "success": False,
                "error": f"Workflow file not found: {full_path}",
                "file_path": file_path,
            }

        # Read and parse JSON
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                workflow_data = json.load(f)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in workflow file: {str(e)}",
                "file_path": str(full_path),
            }

        validation_result: Dict[str, Any] = {
            "success": True,
            "file_path": str(full_path),
            "file_size": full_path.stat().st_size,
            "warnings": [],
            "errors": [],
        }

        # Type-safe access to lists
        errors: List[str] = validation_result["errors"]

        # Validate structure
        if isinstance(workflow_data, list):
            validation_result["workflows_count"] = len(workflow_data)
            validation_result["structure"] = "array"

            # Validate each workflow in the array
            for i, workflow in enumerate(workflow_data):
                if not isinstance(workflow, dict):
                    errors.append(f"Workflow {i} is not a dictionary")
                    continue

                # Check required fields
                required_fields = ["name", "states"]
                for field in required_fields:
                    if field not in workflow:
                        errors.append(f"Workflow {i} missing required field: {field}")

                # Check states structure
                if "states" in workflow and isinstance(workflow["states"], dict):
                    for state_name, state_data in workflow["states"].items():
                        if not isinstance(state_data, dict):
                            errors.append(
                                f"Workflow {i}, state '{state_name}' is not a dictionary"
                            )
                        elif "transitions" in state_data and not isinstance(
                            state_data["transitions"], list
                        ):
                            errors.append(
                                f"Workflow {i}, state '{state_name}' transitions must be an array"
                            )

        elif isinstance(workflow_data, dict):
            validation_result["workflows_count"] = 1
            validation_result["structure"] = "single_object"

            # Check required fields for single workflow
            required_fields = ["name", "states"]
            for field in required_fields:
                if field not in workflow_data:
                    errors.append(f"Workflow missing required field: {field}")

            # Check states structure
            if "states" in workflow_data and isinstance(workflow_data["states"], dict):
                for state_name, state_data in workflow_data["states"].items():
                    if not isinstance(state_data, dict):
                        errors.append(f"State '{state_name}' is not a dictionary")
                    elif "transitions" in state_data and not isinstance(
                        state_data["transitions"], list
                    ):
                        errors.append(
                            f"State '{state_name}' transitions must be an array"
                        )
        else:
            errors.append(
                "Workflow file must contain either a workflow object or array of workflows"
            )

        # Set overall success based on errors
        validation_result["success"] = len(errors) == 0
        validation_result["is_valid"] = validation_result["success"]

        if ctx:
            if validation_result["success"]:
                await ctx.info(
                    f"Workflow file is valid: {validation_result['workflows_count']} workflows found"
                )
            else:
                await ctx.error(
                    f"Workflow file validation failed: {len(errors)} errors found"
                )

        return validation_result

    except Exception as e:
        error_msg = f"Failed to validate workflow file: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "file_path": file_path,
        }
