"""
CreatePermissionProcessor for Cyoda Client Application

Handles the creation and activation of permissions
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.permission.version_1.permission import Permission
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CreatePermissionProcessor(CyodaProcessor):
    """
    Processor for creating and activating Permission entities.
    Initializes permission in active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreatePermissionProcessor",
            description="Creates and activates permission for role assignment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Permission creation according to functional requirements.

        Args:
            entity: The Permission entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed permission in active state
        """
        try:
            self.logger.info(
                f"Creating Permission {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Permission for type-safe operations
            permission = cast_entity(entity, Permission)

            # Set permission as active immediately upon creation
            permission.is_active = True
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Update timestamps
            if not permission.created_at:
                permission.created_at = current_timestamp

            # Validate resource-action combination
            self._validate_resource_action_combination(permission)

            # Log permission creation
            self.logger.info(
                f"Permission {permission.name} created successfully for {permission.resource}.{permission.action}"
            )

            return permission

        except Exception as e:
            self.logger.error(
                f"Error creating permission {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_resource_action_combination(self, permission: Permission) -> None:
        """
        Validate that the resource-action combination is valid.

        Args:
            permission: The permission to validate
        """
        # Basic validation - ensure resource and action are compatible
        resource = permission.resource.lower()
        action = permission.action.lower()

        # Define some basic validation rules
        if resource == "system" and action not in ["admin", "manage", "read"]:
            raise ValueError(f"Invalid action '{action}' for system resource")

        if action == "admin" and resource not in [
            "system",
            "user",
            "role",
            "permission",
        ]:
            raise ValueError(f"Admin action not allowed for resource '{resource}'")

        self.logger.debug(f"Resource-action combination validated: {resource}.{action}")
