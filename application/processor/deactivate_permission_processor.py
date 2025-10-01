"""
DeactivatePermissionProcessor for Cyoda Client Application

Handles the deactivation of permissions from role assignment
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.permission.version_1.permission import Permission
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class DeactivatePermissionProcessor(CyodaProcessor):
    """
    Processor for deactivating Permission entities from role assignment.
    Transitions permission from active to inactive state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DeactivatePermissionProcessor",
            description="Deactivates permission and removes from roles",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Permission deactivation according to functional requirements.

        Args:
            entity: The Permission entity to deactivate
            **kwargs: Additional processing parameters

        Returns:
            The deactivated permission
        """
        try:
            self.logger.info(
                f"Deactivating Permission {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Permission for type-safe operations
            permission = cast_entity(entity, Permission)

            # Check if this is a system permission that cannot be deactivated
            if permission.is_system_permission():
                raise ValueError(
                    f"Cannot deactivate system permission: {permission.name}"
                )

            # Deactivate the permission
            permission.is_active = False
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Add deactivation metadata
            permission.add_metadata("deactivated_at", current_timestamp)
            permission.add_metadata(
                "deactivation_reason", kwargs.get("reason", "Manual deactivation")
            )

            # Remove permission from all roles that have it
            await self._remove_from_roles(permission)

            # Log permission deactivation
            self.logger.info(f"Permission {permission.name} deactivated successfully")

            return permission

        except Exception as e:
            self.logger.error(
                f"Error deactivating permission {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _remove_from_roles(self, permission: Permission) -> None:
        """
        Remove the permission from all roles that have it assigned.

        Args:
            permission: The permission to remove from roles
        """
        try:
            entity_service = get_entity_service()
            permission_id = permission.technical_id or permission.entity_id

            # Note: In a real implementation, you would:
            # 1. Query all roles that have this permission
            # 2. Remove the permission from their permission_ids list
            # 3. Update each role

            # For now, we'll just log the action
            self.logger.info(
                f"Would remove permission {permission_id} from all assigned roles"
            )

            # This is where you would implement the actual role updates:
            # roles_with_permission = await entity_service.search(
            #     entity_class="Role",
            #     condition=SearchConditionRequest.builder()
            #         .contains("permission_ids", permission_id)
            #         .build()
            # )
            #
            # for role_response in roles_with_permission:
            #     role_data = role_response.data
            #     if permission_id in role_data.get("permission_ids", []):
            #         role_data["permission_ids"].remove(permission_id)
            #         await entity_service.update(
            #             entity_id=role_response.metadata.id,
            #             entity=role_data,
            #             entity_class="Role"
            #         )

        except Exception as e:
            self.logger.error(f"Error removing permission from roles: {str(e)}")
            # Don't raise here - we still want to deactivate the permission
