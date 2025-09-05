"""
Workflow Repository Implementation

Repository for interacting with Cyoda Workflow API endpoints.
Provides operations for exporting and importing entity workflows.
"""

import json
import logging
import threading
from typing import Any, Dict, List
from dataclasses import dataclass

from common.utils.utils import send_cyoda_request, custom_serializer

logger = logging.getLogger(__name__)


@dataclass
class WorkflowExportResponse:
    """Response from workflow export operation."""
    entity_name: str
    model_version: str
    workflows: List[Dict[str, Any]]
    
    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> 'WorkflowExportResponse':
        """Create WorkflowExportResponse from API response data."""
        return cls(
            entity_name=response_data.get('entityName', ''),
            model_version=str(response_data.get('modelVersion', '')),
            workflows=response_data.get('workflows', [])
        )


@dataclass
class WorkflowImportRequest:
    """Request for workflow import operation."""
    workflows: List[Dict[str, Any]]
    import_mode: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        return {
            "workflows": self.workflows,
            "importMode": self.import_mode
        }


class WorkflowRepository:
    """
    Repository for workflow operations using Cyoda API.
    Thread-safe singleton implementation.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, cyoda_auth_service):
        """Thread-safe singleton implementation."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._cyoda_auth_service = cyoda_auth_service
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, cyoda_auth_service):
        """Initialize the repository."""
        if not self._initialized:
            self._cyoda_auth_service = cyoda_auth_service
            self._initialized = True
            logger.info("WorkflowRepository initialized")
    
    async def export_entity_workflows(
        self, 
        entity_name: str, 
        model_version: str
    ) -> WorkflowExportResponse:
        """
        Export entity workflows.
        
        Args:
            entity_name: Name of the entity
            model_version: Version of the model
            
        Returns:
            WorkflowExportResponse object
            
        Raises:
            Exception: If the API request fails
        """
        try:
            path = f"model/{entity_name}/{model_version}/workflow/export"
            
            logger.info(f"Exporting workflows for entity {entity_name} version {model_version}")
            
            response = await send_cyoda_request(
                cyoda_auth_service=self._cyoda_auth_service,
                method="get",
                path=path
            )
            
            if response.get('status') != 200:
                logger.error(f"Failed to export workflows: {response}")
                raise Exception(f"Failed to export workflows: {response.get('json')}")
            
            response_data = response.get("json", {})
            workflow_export = WorkflowExportResponse.from_api_response(response_data)
            
            logger.info(f"Successfully exported {len(workflow_export.workflows)} workflows for {entity_name}")
            return workflow_export
            
        except Exception as e:
            logger.exception(f"Error exporting workflows for {entity_name} v{model_version}: {e}")
            raise
    
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
            Dictionary containing import result
            
        Raises:
            Exception: If the API request fails
        """
        try:
            path = f"model/{entity_name}/{model_version}/workflow/import"
            
            # Create import request
            import_request = WorkflowImportRequest(
                workflows=workflows,
                import_mode=import_mode
            )
            
            data = json.dumps(import_request.to_dict(), default=custom_serializer)
            
            logger.info(f"Importing {len(workflows)} workflows for entity {entity_name} version {model_version}")
            
            response = await send_cyoda_request(
                cyoda_auth_service=self._cyoda_auth_service,
                method="post",
                path=path,
                data=data
            )
            
            if response.get('status') != 200:
                logger.error(f"Failed to import workflows: {response}")
                raise Exception(f"Failed to import workflows: {response.get('json')}")
            
            result = response.get("json", {})
            logger.info(f"Successfully imported {len(workflows)} workflows for {entity_name}")
            return result
            
        except Exception as e:
            logger.exception(f"Error importing workflows for {entity_name} v{model_version}: {e}")
            raise
    
    async def validate_workflow_definitions(
        self, 
        workflows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate workflow definitions (basic client-side validation).
        
        Args:
            workflows: List of workflow definitions to validate
            
        Returns:
            Dictionary containing validation result
        """
        try:
            if not workflows:
                return {
                    "valid": False,
                    "error": "No workflows provided for validation",
                    "workflow_count": 0
                }
            
            if not isinstance(workflows, list):
                return {
                    "valid": False,
                    "error": "Workflows must be provided as a list",
                    "workflow_count": 0
                }
            
            # Basic validation - check if each workflow is a dictionary
            validation_errors = []
            for i, workflow in enumerate(workflows):
                if not isinstance(workflow, dict):
                    validation_errors.append(f"Workflow at index {i} is not a dictionary")
                elif not workflow:
                    validation_errors.append(f"Workflow at index {i} is empty")
            
            if validation_errors:
                return {
                    "valid": False,
                    "error": "Invalid workflow format",
                    "validation_errors": validation_errors,
                    "workflow_count": len(workflows)
                }
            
            logger.info(f"Validated {len(workflows)} workflow definitions successfully")
            
            return {
                "valid": True,
                "workflow_count": len(workflows),
                "message": f"All {len(workflows)} workflows passed basic validation"
            }
            
        except Exception as e:
            logger.exception(f"Failed to validate workflows: {e}")
            return {
                "valid": False,
                "error": str(e),
                "workflow_count": len(workflows) if workflows else 0
            }
    
    async def get_workflow_count(
        self, 
        entity_name: str, 
        model_version: str
    ) -> int:
        """
        Get the count of workflows for an entity (convenience method).
        
        Args:
            entity_name: Name of the entity
            model_version: Version of the model
            
        Returns:
            Number of workflows
            
        Raises:
            Exception: If the API request fails
        """
        try:
            export_result = await self.export_entity_workflows(entity_name, model_version)
            return len(export_result.workflows)
        except Exception as e:
            logger.exception(f"Failed to get workflow count for {entity_name} v{model_version}: {e}")
            raise
