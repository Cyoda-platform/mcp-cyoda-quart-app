#!/usr/bin/env python3
"""
Standalone Workflow Import Script

This script allows users to manually import workflows without using MCP tools.
It provides a command-line interface for importing workflow definitions from JSON files.

Usage:
    python scripts/import_workflows.py --entity ExampleEntity --version 1 --file path/to/workflow.json
    python scripts/import_workflows.py --help
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from services.services import get_workflow_management_service

# Add the project root to the path so we can import from the main app
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_workflow_file(file_path: Path) -> Dict[str, Any]:
    """
    Validate a workflow file for correct JSON structure and required fields.

    Args:
        file_path: Path to the workflow file

    Returns:
        Dictionary containing validation result
    """
    try:
        # Check if file exists
        if not file_path.exists():
            return {
                "success": False,
                "error": f"Workflow file not found: {file_path}",
            }

        # Read and parse JSON
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                workflow_data = json.load(f)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON in workflow file: {str(e)}",
            }

        validation_result: Dict[str, Any] = {
            "success": True,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "warnings": [],
            "errors": [],
        }

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

        elif isinstance(workflow_data, dict):
            validation_result["workflows_count"] = 1
            validation_result["structure"] = "single_object"

            # Check required fields for single workflow
            required_fields = ["name", "states"]
            for field in required_fields:
                if field not in workflow_data:
                    errors.append(f"Workflow missing required field: {field}")
        else:
            errors.append(
                "Workflow file must contain either a workflow object or array of workflows"
            )

        # Set overall success based on errors
        validation_result["success"] = len(errors) == 0
        validation_result["workflows"] = workflow_data

        return validation_result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to validate workflow file: {str(e)}",
        }


async def import_workflows_from_file(
    entity_name: str,
    model_version: str,
    file_path: str,
    import_mode: str = "REPLACE",
) -> Dict[str, Any]:
    """
    Import entity workflows from a JSON file.

    Args:
        entity_name: Name of the entity
        model_version: Version of the model
        file_path: Path to the workflow file
        import_mode: Import mode ("REPLACE" or other supported modes)

    Returns:
        Dictionary containing import result
    """
    try:
        logger.info(
            f"Importing workflows for entity {entity_name} version {model_version} from {file_path}"
        )

        # Resolve file path (relative to project root if not absolute)
        if not os.path.isabs(file_path):
            full_path = project_root / file_path
        else:
            full_path = Path(file_path)

        # Validate the workflow file first
        validation_result = validate_workflow_file(full_path)
        if not validation_result["success"]:
            return validation_result

        workflows_data = validation_result["workflows"]
        workflows = (
            workflows_data if isinstance(workflows_data, list) else [workflows_data]
        )

        logger.info(f"Loaded {len(workflows)} workflows from {full_path}")

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
            logger.info(
                f"Successfully imported {len(workflows)} workflows from {full_path}"
            )
        else:
            logger.error(
                f"Failed to import workflows: {import_result.get('error', 'Unknown error')}"
            )

        return import_result

    except Exception as e:
        error_msg = f"Failed to import workflows from file: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "entity_name": entity_name,
            "model_version": model_version,
            "file_path": file_path,
        }


def list_workflow_files(
    base_path: str = "application/resources/workflow",
) -> Dict[str, Any]:
    """
    List available workflow files in the specified directory.

    Args:
        base_path: Base directory to search for workflow files

    Returns:
        Dictionary containing list of workflow files
    """
    try:
        logger.info(f"Listing workflow files in {base_path}")

        # Resolve base path (relative to project root if not absolute)
        if not os.path.isabs(base_path):
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

            workflow_files.append(entity_info)

        # Sort by entity name and version
        workflow_files.sort(
            key=lambda x: (
                x.get("entity_name", ""),
                x.get("model_version", ""),
                x.get("file_name", ""),
            )
        )

        logger.info(f"Found {len(workflow_files)} workflow files")

        return {
            "success": True,
            "base_path": str(full_base_path),
            "files_count": len(workflow_files),
            "workflow_files": workflow_files,
        }

    except Exception as e:
        error_msg = f"Failed to list workflow files: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "base_path": base_path,
        }


def print_workflow_files(workflow_files: List[Dict[str, Any]]) -> None:
    """Print workflow files in a user-friendly format."""
    if not workflow_files:
        print("No workflow files found.")
        return

    print(f"\nFound {len(workflow_files)} workflow files:")
    print("-" * 80)

    for file_info in workflow_files:
        entity_name = file_info.get("entity_name", "Unknown")
        model_version = file_info.get("model_version", "Unknown")
        file_path = file_info.get("relative_path", file_info.get("file_path", ""))
        size = file_info.get("size_bytes", 0)

        print(f"Entity: {entity_name}")
        print(f"Version: {model_version}")
        print(f"File: {file_path}")
        print(f"Size: {size} bytes")
        print("-" * 40)


async def main() -> None:
    """Main function to handle command line arguments and execute workflow import."""
    parser = argparse.ArgumentParser(
        description="Import workflows from JSON files to Cyoda platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import a specific workflow
  python scripts/import_workflows.py --entity ExampleEntity --version 1 --file example_application/resources/workflow/exampleentity/version_1/ExampleEntity.json
  # Import with custom mode
  python scripts/import_workflows.py --entity MyEntity --version 2 --file path/to/workflow.json --mode MERGE
  # List available workflow files
  python scripts/import_workflows.py --list
  # List workflow files in custom directory
  python scripts/import_workflows.py --list --base-path custom/workflow/directory
        """,
    )

    parser.add_argument(
        "--entity", "-e", help="Entity name (must match ENTITY_NAME in entity class)"
    )

    parser.add_argument(
        "--version", "-v", default="1", help="Model version (default: 1)"
    )

    parser.add_argument(
        "--file",
        "-f",
        help="Path to workflow JSON file (relative to project root or absolute)",
    )

    parser.add_argument(
        "--mode", "-m", default="REPLACE", help="Import mode (default: REPLACE)"
    )

    parser.add_argument(
        "--list", "-l", action="store_true", help="List available workflow files"
    )

    parser.add_argument(
        "--base-path",
        "-b",
        default="application/resources/workflow",
        help="Base path for listing workflow files (default: application/resources/workflow)",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the workflow file without importing",
    )

    args = parser.parse_args()

    # Handle list command
    if args.list:
        result = list_workflow_files(args.base_path)
        if result["success"]:
            print_workflow_files(result["workflow_files"])
        else:
            print(f"Error: {result['error']}")
            sys.exit(1)
        return

    # Validate required arguments for import
    if not args.entity or not args.file:
        parser.error("--entity and --file are required for import operations")

    # Handle validate-only command
    if args.validate_only:
        file_path = (
            project_root / args.file
            if not os.path.isabs(args.file)
            else Path(args.file)
        )
        result = validate_workflow_file(file_path)

        if result["success"]:
            print("✅ Workflow file is valid!")
            print(f"   File: {result['file_path']}")
            print(f"   Size: {result['file_size']} bytes")
            print(f"   Workflows: {result['workflows_count']}")
            print(f"   Structure: {result['structure']}")
        else:
            print("❌ Workflow file validation failed!")
            if result.get("error"):
                print(f"   Error: {result['error']}")
            if result.get("errors"):
                print("   Validation errors:")
                for error in result["errors"]:
                    print(f"     - {error}")
            sys.exit(1)
        return

    # Import workflows
    print(f"Importing workflows for {args.entity} version {args.version}...")
    print(f"File: {args.file}")
    print(f"Mode: {args.mode}")
    print()

    result = await import_workflows_from_file(
        entity_name=args.entity,
        model_version=args.version,
        file_path=args.file,
        import_mode=args.mode,
    )

    if result["success"]:
        print("✅ Workflow import successful!")
        print(f"   Entity: {args.entity}")
        print(f"   Version: {args.version}")
        print(f"   File: {result.get('file_path', args.file)}")
        print(f"   Workflows loaded: {result.get('workflows_loaded', 'Unknown')}")
        if result.get("message"):
            print(f"   Message: {result['message']}")
    else:
        print("❌ Workflow import failed!")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
