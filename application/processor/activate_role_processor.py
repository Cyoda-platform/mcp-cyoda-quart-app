"""
ActivateRoleProcessor for Cyoda Client Application

Handles the activation of roles for user assignment
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.role.version_1.role import Role
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ActivateRoleProcessor(CyodaProcessor):
    """
    Processor for activating Role entities for user assignment.
    Transitions role from draft to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ActivateRoleProcessor",
            description="Activates role for user assignment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Role activation according to functional requirements.

        Args:
            entity: The Role entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated role
        """
        try:
            self.logger.info(
                f"Activating Role {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Role for type-safe operations
            role = cast_entity(entity, Role)

            # Activate the role
            role.is_active = True
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            role.updated_at = current_timestamp

            # Add activation metadata
            role.add_metadata("activated_at", current_timestamp)
            role.add_metadata("activation_method", "manual")

            # Log role activation
            self.logger.info(f"Role {role.name} activated successfully")

            return role

        except Exception as e:
            self.logger.error(
                f"Error activating role {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
