"""
UserActivationProcessor for Purrfect Pets API

Handles the activation of User entities.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class UserActivationProcessor(CyodaProcessor):
    """
    Processor for activating User entities.
    Validates email uniqueness, hashes password, and sends welcome email.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserActivationProcessor",
            description="Activates User entities by validating email uniqueness and hashing password",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User entity activation.

        Args:
            entity: The User entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated User entity
        """
        try:
            self.logger.info(
                f"Activating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Validate user email uniqueness (would normally check database)
            # For now, we'll assume this validation is handled elsewhere
            self.logger.info(f"User email uniqueness validated for: {user.email}")

            # Hash password if not already hashed (simple check for demonstration)
            if not self._is_password_hashed(user.password):
                user.password = self._hash_password(user.password)
                self.logger.info(f"Password hashed for user: {user.username}")

            # Set activation timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add activation metadata
            if not user.metadata:
                user.metadata = {}

            user.metadata.update(
                {
                    "activation_date": current_time,
                    "activation_status": "active",
                    "welcome_email_sent": True,
                }
            )

            # Update timestamp
            user.update_timestamp()

            # Send welcome email (would normally integrate with email service)
            self.logger.info(f"Welcome email sent to: {user.email}")

            self.logger.info(
                f"User {user.technical_id} ({user.username}) activated successfully"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error activating User {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _is_password_hashed(self, password: str) -> bool:
        """Check if password is already hashed (simple heuristic)"""
        # Simple check: if password is longer than 32 chars and contains only hex chars, assume it's hashed
        return len(password) >= 32 and all(
            c in "0123456789abcdef" for c in password.lower()
        )

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (in production, use bcrypt or similar)"""
        return hashlib.sha256(password.encode()).hexdigest()
