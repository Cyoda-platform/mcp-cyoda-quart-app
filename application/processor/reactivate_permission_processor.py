"""
ReactivatePermissionProcessor for Cyoda Client Application

Handles the reactivation of permissions for role assignment
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.permission.version_1.permission import Permission
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReactivatePermissionProcessor(CyodaProcessor):
    """
    Processor for reactivating Permission entities for role assignment.
    Transitions permission from inactive back to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReactivatePermissionProcessor",
            description="Reactivates permission for role assignment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Permission reactivation according to functional requirements.

        Args:
            entity: The Permission entity to reactivate
            **kwargs: Additional processing parameters

        Returns:
            The reactivated permission
        """
        try:
            self.logger.info(
                f"Reactivating Permission {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Permission for type-safe operations
            permission = cast_entity(entity, Permission)

            # Reactivate the permission
            permission.is_active = True
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Add reactivation metadata
            permission.add_metadata("reactivated_at", current_timestamp)
            permission.add_metadata(
                "reactivation_reason", kwargs.get("reason", "Manual reactivation")
            )

            # Clear previous deactivation metadata
            if permission.metadata and "deactivated_at" in permission.metadata:
                permission.add_metadata(
                    "previous_deactivation_cleared",
                    permission.metadata.get("deactivated_at"),
                )

            # Log permission reactivation
            self.logger.info(f"Permission {permission.name} reactivated successfully")

            return permission

        except Exception as e:
            self.logger.error(
                f"Error reactivating permission {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
