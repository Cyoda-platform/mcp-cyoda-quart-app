"""
ReactivateRoleProcessor for Cyoda Client Application

Handles the reactivation of roles for assignment
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.role.version_1.role import Role


class ReactivateRoleProcessor(CyodaProcessor):
    """
    Processor for reactivating Role entities for assignment.
    Transitions role from inactive back to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReactivateRoleProcessor",
            description="Reactivates role for user assignment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Role reactivation according to functional requirements.

        Args:
            entity: The Role entity to reactivate
            **kwargs: Additional processing parameters

        Returns:
            The reactivated role
        """
        try:
            self.logger.info(
                f"Reactivating Role {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Role for type-safe operations
            role = cast_entity(entity, Role)

            # Reactivate the role
            role.is_active = True
            current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            role.updated_at = current_timestamp

            # Add reactivation metadata
            role.add_metadata("reactivated_at", current_timestamp)
            role.add_metadata("reactivation_reason", kwargs.get("reason", "Manual reactivation"))

            # Clear previous deactivation metadata
            if role.metadata and "deactivated_at" in role.metadata:
                role.add_metadata("previous_deactivation_cleared", role.metadata.get("deactivated_at"))

            # Log role reactivation
            self.logger.info(
                f"Role {role.name} reactivated successfully"
            )

            return role

        except Exception as e:
            self.logger.error(
                f"Error reactivating role {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
