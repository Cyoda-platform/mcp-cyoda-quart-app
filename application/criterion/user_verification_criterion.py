"""
UserVerificationCriterion for Purrfect Pets API

Validates user verification token and eligibility according to criteria.md specification.
"""

from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class UserVerificationCriterion(CyodaCriteriaChecker):
    """
    Verification criterion for User that validates user verification token and eligibility.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserVerificationCriterion",
            description="Validates user verification token and eligibility",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the user verification is valid.

        Args:
            entity: The CyodaEntity to validate (expected to be User)
            **kwargs: Additional criteria parameters including verification_token

        Returns:
            True if verification is valid, False otherwise
        """
        try:
            self.logger.info(
                f"Checking verification for user {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Get verification token from kwargs
            verification_token = kwargs.get("verification_token")

            # Check if verification token is null or empty
            if not verification_token:
                self.logger.warning(
                    f"User {user.technical_id} verification token is null or empty"
                )
                return False

            # Check if user has verification data
            if not user.metadata or "verification" not in user.metadata:
                self.logger.warning(
                    f"User {user.technical_id} has no verification data"
                )
                return False

            verification_data = user.metadata["verification"]

            # Check if verification token is expired
            expires_at = verification_data.get("expires_at")
            if expires_at:
                try:
                    expiry_dt = datetime.fromisoformat(
                        expires_at.replace("Z", "+00:00")
                    )
                    if datetime.now(timezone.utc) > expiry_dt:
                        self.logger.warning(
                            f"User {user.technical_id} verification token is expired"
                        )
                        return False
                except ValueError:
                    self.logger.warning(
                        f"User {user.technical_id} has invalid expiry date format"
                    )
                    return False

            # Check if verification token matches user
            stored_token = verification_data.get("token")
            if stored_token != verification_token:
                self.logger.warning(
                    f"User {user.technical_id} verification token does not match"
                )
                return False

            # Check if user state is PENDING_VERIFICATION
            if user.state != "pending_verification":
                self.logger.warning(
                    f"User {user.technical_id} is not in PENDING_VERIFICATION state, current state: {user.state}"
                )
                return False

            self.logger.info(f"User {user.technical_id} passed verification check")
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking user verification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
