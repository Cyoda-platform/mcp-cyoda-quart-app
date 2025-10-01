"""
DeactivateRoleProcessor for Cyoda Client Application

Handles the deactivation of roles from assignment
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.role.version_1.role import Role
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class DeactivateRoleProcessor(CyodaProcessor):
    """
    Processor for deactivating Role entities from assignment.
    Transitions role from active to inactive state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DeactivateRoleProcessor",
            description="Deactivates role from user assignment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Role deactivation according to functional requirements.

        Args:
            entity: The Role entity to deactivate
            **kwargs: Additional processing parameters

        Returns:
            The deactivated role
        """
        try:
            self.logger.info(
                f"Deactivating Role {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Role for type-safe operations
            role = cast_entity(entity, Role)

            # Deactivate the role
            role.is_active = False
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            role.updated_at = current_timestamp

            # Add deactivation metadata
            role.add_metadata("deactivated_at", current_timestamp)
            role.add_metadata(
                "deactivation_reason", kwargs.get("reason", "Manual deactivation")
            )

            # Log role deactivation
            self.logger.info(f"Role {role.name} deactivated successfully")

            # Note: In a real implementation, you would:
            # - Check if role is assigned to any users
            # - Send notifications about role deactivation
            # - Log deactivation event for audit trail

            return role

        except Exception as e:
            self.logger.error(
                f"Error deactivating role {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
