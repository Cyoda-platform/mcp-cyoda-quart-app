"""
UserVerificationCriterion for Cyoda Client Application

Validates that a user can be activated (email verification completed)
as specified in functional requirements.
"""

from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class UserVerificationCriterion(CyodaCriteriaChecker):
    """
    Verification criterion for User that checks if user can be activated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserVerificationCriterion",
            description="Validates User can be activated after verification",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the user can be activated.

        Args:
            entity: The CyodaEntity to validate (expected to be User)
            **kwargs: Additional criteria parameters

        Returns:
            True if the user can be activated, False otherwise
        """
        try:
            self.logger.info(
                f"Validating User verification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Check email verification (placeholder implementation)
            if not self._is_email_verified(user.email):
                self.logger.warning(
                    f"Email verification not completed for user {user.technical_id}"
                )
                return False

            # Check username uniqueness (placeholder implementation)
            if not await self._is_username_unique(
                user.username, user.technical_id or user.entity_id
            ):
                self.logger.warning(f"Username {user.username} is no longer unique")
                return False

            # Check email uniqueness (placeholder implementation)
            if not await self._is_email_unique(
                user.email, user.technical_id or user.entity_id
            ):
                self.logger.warning(f"Email {user.email} is no longer unique")
                return False

            self.logger.info(
                f"User {user.technical_id} passed all verification criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating User verification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _is_email_verified(self, email: str) -> bool:
        """
        Check if email is verified (placeholder implementation).

        Args:
            email: The email address to check

        Returns:
            True if email is verified, False otherwise
        """
        try:
            # In a real implementation, this would check against verification service
            # For now, we'll assume all emails are verified for testing
            self.logger.info(f"Checking email verification for {email}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to check email verification for {email}: {str(e)}"
            )
            return False

    async def _is_username_unique(self, username: str, user_id: str) -> bool:
        """
        Check if username is unique (placeholder implementation).

        Args:
            username: The username to check
            user_id: The current user ID (to exclude from uniqueness check)

        Returns:
            True if username is unique, False otherwise
        """
        try:
            # In a real implementation, this would search for other users with same username
            # For now, we'll assume all usernames are unique for testing
            self.logger.info(f"Checking username uniqueness for {username}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to check username uniqueness for {username}: {str(e)}"
            )
            return False

    async def _is_email_unique(self, email: str, user_id: str) -> bool:
        """
        Check if email is unique (placeholder implementation).

        Args:
            email: The email to check
            user_id: The current user ID (to exclude from uniqueness check)

        Returns:
            True if email is unique, False otherwise
        """
        try:
            # In a real implementation, this would search for other users with same email
            # For now, we'll assume all emails are unique for testing
            self.logger.info(f"Checking email uniqueness for {email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to check email uniqueness for {email}: {str(e)}")
            return False
