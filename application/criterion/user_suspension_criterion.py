"""
UserSuspensionCriterion for Cyoda Client Application

Validates that a user can be suspended as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.user.version_1.user import User


class UserSuspensionCriterion(CyodaCriteriaChecker):
    """
    Suspension criterion for User that checks if user can be suspended.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserSuspensionCriterion",
            description="Validates User can be suspended",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the user can be suspended.

        Args:
            entity: The CyodaEntity to validate (expected to be User)
            **kwargs: Additional criteria parameters (should include reason)

        Returns:
            True if the user can be suspended, False otherwise
        """
        try:
            self.logger.info(f"Validating User suspension {getattr(entity, 'technical_id', '<unknown>')}")

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Get suspension reason from kwargs
            reason = kwargs.get("reason")
            if not reason or not reason.strip():
                self.logger.warning(f"Suspension reason must be provided for user {user.technical_id}")
                return False

            # Check if user is admin (admins cannot be suspended)
            if user.is_admin_user():
                self.logger.warning(f"Admin users cannot be suspended: {user.username}")
                return False

            self.logger.info(f"User {user.technical_id} can be suspended")
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating User suspension {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
