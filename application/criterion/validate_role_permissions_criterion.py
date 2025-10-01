"""
ValidateRolePermissions Criterion for Cyoda Client Application

Validates that a Role has valid permissions before activation
as specified in functional requirements.
"""

from typing import Any

from application.entity.role.version_1.role import Role
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ValidateRolePermissions(CyodaCriteriaChecker):
    """
    Validation criterion for Role that checks if role has valid permissions
    before it can be activated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidateRolePermissions",
            description="Validates that role has valid permissions for activation",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the role has valid permissions for activation.

        Args:
            entity: The CyodaEntity to validate (expected to be Role)
            **kwargs: Additional criteria parameters

        Returns:
            True if the role has valid permissions, False otherwise
        """
        try:
            self.logger.info(
                f"Validating permissions for role {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Role for type-safe operations
            role = cast_entity(entity, Role)

            # Check if role has at least one permission
            if not role.permission_ids or len(role.permission_ids) == 0:
                self.logger.warning(f"Role {role.name} has no permissions assigned")
                return False

            # Validate that all permission IDs are non-empty strings
            for permission_id in role.permission_ids:
                if (
                    not permission_id
                    or not isinstance(permission_id, str)
                    or len(permission_id.strip()) == 0
                ):
                    self.logger.warning(
                        f"Role {role.name} has invalid permission ID: {permission_id}"
                    )
                    return False

            # Check for duplicate permission IDs
            if len(role.permission_ids) != len(set(role.permission_ids)):
                self.logger.warning(f"Role {role.name} has duplicate permission IDs")
                return False

            self.logger.info(
                f"Role {role.name} passed permission validation with {len(role.permission_ids)} permissions"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating role permissions {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
