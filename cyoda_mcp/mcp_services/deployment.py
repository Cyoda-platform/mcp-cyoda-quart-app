"""
Deployment Service for MCP

This service provides deployment functionality for the MCP server,
using the DeploymentRepository for AI Host API operations.
"""

import logging
from typing import Dict, Any, Optional
from common.repository.cyoda.deployment_repository import DeploymentRepository

logger = logging.getLogger(__name__)


class DeploymentService:
    """Service class for deployment operations."""
    
    def __init__(self, deployment_repository: DeploymentRepository):
        """
        Initialize the deployment service.
        
        Args:
            deployment_repository: The injected deployment repository
        """
        self.deployment_repository = deployment_repository
        logger.info("DeploymentService initialized")
    
    async def schedule_deploy_env(
        self,
        technical_id: str
    ) -> Dict[str, Any]:
        """
        Schedule environment deployment.
        
        Args:
            technical_id: Technical ID of the environment
            user_id: User ID initiating the deployment
            entity_data: Entity data for deployment
            
        Returns:
            Dictionary containing deployment result or error information
        """
        try:
            if not self.deployment_repository:
                return {
                    "success": False,
                    "error": "Deployment repository not available",
                    "technical_id": technical_id
                }
            
            result = await self.deployment_repository.schedule_deploy_env(
                technical_id=technical_id
            )
            
            logger.info(f"Successfully scheduled environment deployment for {technical_id}")
            
            return {
                "success": result.success,
                "message": result.message,
                "build_id": result.build_id,
                "status": result.status,
                "technical_id": technical_id,
                "data": result.data
            }
            
        except Exception as e:
            logger.exception(f"Failed to schedule environment deployment for {technical_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "technical_id": technical_id
            }
    
    async def schedule_build_user_application(
        self,
        technical_id: str,
        user_id: str = None,
        entity_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Schedule user application build.
        
        Args:
            technical_id: Technical ID of the application
            user_id: User ID initiating the build
            entity_data: Entity data for build
            
        Returns:
            Dictionary containing build result or error information
        """
        try:
            if not self.deployment_repository:
                return {
                    "success": False,
                    "error": "Deployment repository not available",
                    "technical_id": technical_id
                }
            
            result = await self.deployment_repository.schedule_build_user_application(
                technical_id=technical_id,
                user_id=user_id,
                entity_data=entity_data
            )
            
            logger.info(f"Successfully scheduled user application build for {technical_id}")
            
            return {
                "success": result.success,
                "message": result.message,
                "build_id": result.build_id,
                "status": result.status,
                "technical_id": technical_id,
                "user_id": user_id,
                "data": result.data
            }
            
        except Exception as e:
            logger.exception(f"Failed to schedule user application build for {technical_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "technical_id": technical_id
            }
    
    async def schedule_deploy_user_application(
        self,
        technical_id: str,
        user_id: str = None,
        entity_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Schedule user application deployment.
        
        Args:
            technical_id: Technical ID of the application
            user_id: User ID initiating the deployment
            entity_data: Entity data for deployment
            
        Returns:
            Dictionary containing deployment result or error information
        """
        try:
            if not self.deployment_repository:
                return {
                    "success": False,
                    "error": "Deployment repository not available",
                    "technical_id": technical_id
                }
            
            result = await self.deployment_repository.schedule_deploy_user_application(
                technical_id=technical_id,
                user_id=user_id,
                entity_data=entity_data
            )
            
            logger.info(f"Successfully scheduled user application deployment for {technical_id}")
            
            return {
                "success": result.success,
                "message": result.message,
                "build_id": result.build_id,
                "status": result.status,
                "technical_id": technical_id,
                "user_id": user_id,
                "data": result.data
            }
            
        except Exception as e:
            logger.exception(f"Failed to schedule user application deployment for {technical_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "technical_id": technical_id
            }

    async def get_env_deploy_status(
        self,
        build_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get deployment status for a specific build.

        Args:
            build_id: Build ID to check status for
            user_id: Optional user ID

        Returns:
            Dictionary containing deployment status or error information
        """
        try:
            if not self.deployment_repository:
                return {
                    "success": False,
                    "error": "Deployment repository not available",
                    "build_id": build_id
                }

            result = await self.deployment_repository.get_env_deploy_status(
                build_id=build_id,
                user_id=user_id
            )

            logger.info(f"Successfully retrieved deployment status for build {build_id}")

            return {
                "success": result.success,
                "message": result.message,
                "build_id": build_id,
                "status": result.status,
                "user_id": user_id,
                "data": result.data
            }

        except Exception as e:
            logger.exception(f"Failed to get deployment status for build {build_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "build_id": build_id
            }
