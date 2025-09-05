"""
Workflow Management Service for MCP

This service provides workflow management functionality for the MCP server,
using the CyodaRepository for workflow export/import operations.
"""

import logging
from typing import Dict, Any, List, Optional
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
        self, 
        entity_name: str, 
        model_version: str
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
                    "model_version": model_version
                }

            result = await self.workflow_repository.export_entity_workflows(
                entity_name=entity_name,
                model_version=model_version
            )

            logger.info(f"Successfully exported workflows for {entity_name} v{model_version}")

            return {
                "success": True,
                "entity_name": result.entity_name,
                "model_version": result.model_version,
                "workflows": result.workflows,
                "workflow_count": len(result.workflows)
            }
            
        except Exception as e:
            logger.exception(f"Failed to export workflows for {entity_name} v{model_version}: {e}")
            return {
                "success": False,
                "error": str(e),
                "entity_name": entity_name,
                "model_version": model_version
            }
    
    async def import_entity_workflows(
        self,
        entity_name: str,
        model_version: str,
        workflows: List[Dict[str, Any]],
        import_mode: str = "REPLACE"
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
                    "model_version": model_version
                }

            if not workflows:
                return {
                    "success": False,
                    "error": "No workflows provided for import",
                    "entity_name": entity_name,
                    "model_version": model_version
                }

            result = await self.workflow_repository.import_entity_workflows(
                entity_name=entity_name,
                model_version=model_version,
                workflows=workflows,
                import_mode=import_mode
            )
            
            logger.info(f"Successfully imported {len(workflows)} workflows for {entity_name} v{model_version}")
            
            return {
                "success": True,
                "entity_name": entity_name,
                "model_version": model_version,
                "import_mode": import_mode,
                "workflows_imported": len(workflows),
                "result": result
            }
            
        except Exception as e:
            logger.exception(f"Failed to import workflows for {entity_name} v{model_version}: {e}")
            return {
                "success": False,
                "error": str(e),
                "entity_name": entity_name,
                "model_version": model_version,
                "import_mode": import_mode
            }
    
    async def copy_workflows_between_entities(
        self,
        source_entity_name: str,
        source_model_version: str,
        target_entity_name: str,
        target_model_version: str,
        import_mode: str = "REPLACE"
    ) -> Dict[str, Any]:
        """
        Copy workflows from one entity to another (convenience method).
        
        Args:
            source_entity_name: Name of the source entity
            source_model_version: Version of the source model
            target_entity_name: Name of the target entity
            target_model_version: Version of the target model
            import_mode: Import mode ("REPLACE" or other supported modes)
            
        Returns:
            Dictionary containing copy result or error information
        """
        try:
            # First, export workflows from source
            export_result = await self.export_entity_workflows(
                entity_name=source_entity_name,
                model_version=source_model_version
            )
            
            if not export_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to export from source: {export_result.get('error')}",
                    "source_entity": source_entity_name,
                    "source_version": source_model_version,
                    "target_entity": target_entity_name,
                    "target_version": target_model_version
                }
            
            workflows = export_result.get("workflows", [])
            
            if not workflows:
                return {
                    "success": False,
                    "error": "No workflows found in source entity",
                    "source_entity": source_entity_name,
                    "source_version": source_model_version,
                    "target_entity": target_entity_name,
                    "target_version": target_model_version
                }
            
            # Then, import workflows to target
            import_result = await self.import_entity_workflows(
                entity_name=target_entity_name,
                model_version=target_model_version,
                workflows=workflows,
                import_mode=import_mode
            )
            
            if not import_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to import to target: {import_result.get('error')}",
                    "source_entity": source_entity_name,
                    "source_version": source_model_version,
                    "target_entity": target_entity_name,
                    "target_version": target_model_version
                }
            
            logger.info(f"Successfully copied {len(workflows)} workflows from {source_entity_name} to {target_entity_name}")
            
            return {
                "success": True,
                "source_entity": source_entity_name,
                "source_version": source_model_version,
                "target_entity": target_entity_name,
                "target_version": target_model_version,
                "workflows_copied": len(workflows),
                "import_mode": import_mode
            }
            
        except Exception as e:
            logger.exception(f"Failed to copy workflows from {source_entity_name} to {target_entity_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "source_entity": source_entity_name,
                "source_version": source_model_version,
                "target_entity": target_entity_name,
                "target_version": target_model_version
            }
    
    async def validate_workflows(self, workflows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate workflow definitions using the workflow repository.

        Args:
            workflows: List of workflow definitions to validate

        Returns:
            Dictionary containing validation result
        """
        try:
            if not self.workflow_repository:
                return {
                    "valid": False,
                    "error": "Workflow repository not available",
                    "workflow_count": len(workflows) if workflows else 0
                }

            return await self.workflow_repository.validate_workflow_definitions(workflows)

        except Exception as e:
            logger.exception(f"Failed to validate workflows: {e}")
            return {
                "valid": False,
                "error": str(e),
                "workflow_count": len(workflows) if workflows else 0
            }
