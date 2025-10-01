"""
CreateRoleProcessor for Cyoda Client Application

Handles the creation of new roles with basic settings
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.role.version_1.role import Role
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CreateRoleProcessor(CyodaProcessor):
    """
    Processor for creating new Role entities with basic settings.
    Initializes role in draft state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreateRoleProcessor",
            description="Creates new role with basic settings in draft state",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Role creation according to functional requirements.

        Args:
            entity: The Role entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed role in draft state
        """
        try:
            self.logger.info(
                f"Creating Role {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Role for type-safe operations
            role = cast_entity(entity, Role)

            # Set default values for new role
            role.is_active = False  # Roles start inactive until activated
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Update timestamps
            if not role.created_at:
                role.created_at = current_timestamp
            role.updated_at = current_timestamp

            # Initialize permission_ids if not set
            if role.permission_ids is None:
                role.permission_ids = []

            # Log role creation
            self.logger.info(f"Role {role.name} created successfully in draft state")

            return role

        except Exception as e:
            self.logger.error(
                f"Error creating role {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
