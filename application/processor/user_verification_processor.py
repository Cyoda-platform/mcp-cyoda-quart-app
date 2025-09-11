"""
UserVerificationProcessor for Purrfect Pets API

Verifies user email and activates account according to processors.md specification.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class UserVerificationProcessor(CyodaProcessor):
    """
    Processor for User verification that verifies user email and activates account.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserVerificationProcessor",
            description="Verifies user email and activates account",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User entity verification according to functional requirements.

        Args:
            entity: The User entity to verify
            **kwargs: Additional processing parameters including verification_token

        Returns:
            The verified user entity
        """
        try:
            self.logger.info(
                f"Processing verification for User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Get verification token from kwargs
            verification_token = kwargs.get("verification_token")
            if not verification_token:
                raise ValueError("Verification token is required")

            # Validate verification token
            if not user.metadata or "verification" not in user.metadata:
                raise ValueError("No verification data found for user")

            verification_data = user.metadata["verification"]

            # Check if token matches
            if verification_data.get("token") != verification_token:
                raise ValueError("Invalid verification token")

            # Check token expiry
            expires_at = verification_data.get("expires_at")
            if expires_at:
                expiry_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                if datetime.now(timezone.utc) > expiry_dt:
                    raise ValueError("Verification token has expired")

            # Mark email as verified
            verification_data["verified"] = True
            verification_data["verified_at"] = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Set account activation date
            user.metadata["account_activated_at"] = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Send welcome email (placeholder)
            await self._send_welcome_email(user)

            # Update timestamp
            user.update_timestamp()

            self.logger.info(
                f"User {user.technical_id} verification processed successfully"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error processing user verification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_welcome_email(self, user: User) -> None:
        """Send welcome email to user"""
        try:
            # Placeholder for welcome email sending
            self.logger.info(f"Sent welcome email to {user.email}")

        except Exception as e:
            self.logger.warning(f"Failed to send welcome email: {str(e)}")
            # Don't raise - email failure shouldn't stop verification
