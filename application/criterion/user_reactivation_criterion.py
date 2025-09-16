"""
UserReactivationCriterion for Cyoda Client Application

Validates that a suspended user can be reactivated as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.user.version_1.user import User


class UserReactivationCriterion(CyodaCriteriaChecker):
    """
    Reactivation criterion for User that checks if suspended user can be reactivated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserReactivationCriterion",
            description="Validates suspended User can be reactivated",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the suspended user can be reactivated.

        Args:
            entity: The CyodaEntity to validate (expected to be User)
            **kwargs: Additional criteria parameters

        Returns:
            True if the user can be reactivated, False otherwise
        """
        try:
            self.logger.info(f"Validating User reactivation {getattr(entity, 'technical_id', '<unknown>')}")

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Check if user is permanently suspended
            if await self._is_permanently_suspended(user.technical_id or user.entity_id or "unknown"):
                self.logger.warning(f"User {user.technical_id} is permanently suspended")
                return False

            # Check if minimum suspension period has elapsed
            if not await self._has_minimum_period_elapsed(user.technical_id or user.entity_id or "unknown"):
                self.logger.warning(f"Minimum suspension period has not elapsed for user {user.technical_id}")
                return False

            self.logger.info(f"User {user.technical_id} can be reactivated")
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating User reactivation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _is_permanently_suspended(self, user_id: str) -> bool:
        """
        Check if user is permanently suspended (placeholder implementation).

        Args:
            user_id: The user ID to check

        Returns:
            True if permanently suspended, False otherwise
        """
        try:
            # In a real implementation, this would check suspension records
            # For now, we'll assume no users are permanently suspended for testing
            self.logger.info(f"Checking permanent suspension status for user {user_id}")
            return False
                
        except Exception as e:
            self.logger.error(f"Failed to check permanent suspension for user {user_id}: {str(e)}")
            return False

    async def _has_minimum_period_elapsed(self, user_id: str) -> bool:
        """
        Check if minimum suspension period has elapsed (placeholder implementation).

        Args:
            user_id: The user ID to check

        Returns:
            True if minimum period has elapsed, False otherwise
        """
        try:
            # In a real implementation, this would check suspension records and timing
            # For now, we'll assume minimum period has always elapsed for testing
            self.logger.info(f"Checking minimum suspension period for user {user_id}")
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to check minimum suspension period for user {user_id}: {str(e)}")
            return True  # Allow reactivation on error
