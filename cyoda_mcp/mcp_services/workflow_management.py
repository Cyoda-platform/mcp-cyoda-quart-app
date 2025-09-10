"""
Workflow Management Service for MCP

This service provides workflow management functionality for the MCP server,
using the CyodaRepository for workflow export/import operations.
"""

import logging
from typing import Any, Dict, List

from common.repository.cyoda.workflow_repository import WorkflowRepository

logger = logging.getLogger(__name__)


class WorkflowManagementService:
    """Service class for workflow management operations."""

    def __init__(self, workflow_repository: WorkflowRepository):
        """
        Initialize the workflow management service.

        Args:
            workflow_repository: The injected workflow repository
        """
        self.workflow_repository = workflow_repository
        logger.info("WorkflowManagementService initialized")

    async def export_entity_workflows(
        self, entity_name: str, model_version: str
    ) -> Dict[str, Any]:
        """
        Export entity workflows.

        Args:
            entity_name: Name of the entity
            model_version: Version of the model

        Returns:
            Dictionary containing exported workflows or error information
        """
        try:
            if not self.workflow_repository:
                return {
                    "success": False,
                    "error": "Workflow repository not available",
                    "entity_name": entity_name,
                    "model_version": model_version,
                }

            result = await self.workflow_repository.export_entity_workflows(
                entity_name=entity_name, model_version=model_version
            )

            logger.info(
                f"Successfully exported workflows for {entity_name} v{model_version}"
            )

            return {
                "success": True,
                "entity_name": result.entity_name,
                "model_version": result.model_version,
                "workflows": result.workflows,
                "workflow_count": len(result.workflows),
            }

        except Exception as e:
            logger.exception(
                f"Failed to export workflows for {entity_name} v{model_version}: {e}"
            )
            return {
                "success": False,
                "error": str(e),
                "entity_name": entity_name,
                "model_version": model_version,
            }

    async def import_entity_workflows(
        self,
        entity_name: str,
        model_version: str,
        workflows: List[Dict[str, Any]],
        import_mode: str = "REPLACE",
    ) -> Dict[str, Any]:
        """
        Import entity workflows.

        Args:
            entity_name: Name of the entity
            model_version: Version of the model
            workflows: List of workflow definitions
            import_mode: Import mode ("REPLACE" or other supported modes)

        Returns:
            Dictionary containing import result or error information
        """
        try:
            if not self.workflow_repository:
                return {
                    "success": False,
                    "error": "Workflow repository not available",
                    "entity_name": entity_name,
                    "model_version": model_version,
                }

            if not workflows:
                return {
                    "success": False,
                    "error": "No workflows provided for import",
                    "entity_name": entity_name,
                    "model_version": model_version,
                }

            result = await self.workflow_repository.import_entity_workflows(
                entity_name=entity_name,
                model_version=model_version,
                workflows=workflows,
                import_mode=import_mode,
            )

            logger.info(
                f"Successfully imported {len(workflows)} workflows for {entity_name} v{model_version}"
            )

            return {
                "success": True,
                "entity_name": entity_name,
                "model_version": model_version,
                "import_mode": import_mode,
                "workflows_imported": len(workflows),
                "result": result,
            }

        except Exception as e:
            logger.exception(
                f"Failed to import workflows for {entity_name} v{model_version}: {e}"
            )
            return {
                "success": False,
                "error": str(e),
                "entity_name": entity_name,
                "model_version": model_version,
                "import_mode": import_mode,
            }
