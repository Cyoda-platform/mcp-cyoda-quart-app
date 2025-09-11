"""
UserActivationProcessor for Purrfect Pets API

Activates or reactivates user account according to processors.md specification.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class UserActivationProcessor(CyodaProcessor):
    """
    Processor for User activation that activates or reactivates user account.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserActivationProcessor",
            description="Activates or reactivates user account",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User entity activation according to functional requirements.

        Args:
            entity: The User entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated user entity
        """
        try:
            self.logger.info(
                f"Processing activation for User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Clear suspension flags
            if user.metadata is None:
                user.metadata = {}

            # Remove suspension data if it exists
            if "suspension" in user.metadata:
                old_suspension = user.metadata["suspension"]
                del user.metadata["suspension"]
                self.logger.info(f"Cleared suspension data: {old_suspension}")

            if "suspension_date" in user.metadata:
                del user.metadata["suspension_date"]

            # Set reactivation date
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            user.metadata["reactivation"] = {
                "reactivated_at": current_timestamp,
                "reactivated_by": "system",
            }

            # Send reactivation notification (placeholder)
            await self._send_reactivation_notification(user)

            # Update timestamp
            user.update_timestamp()

            self.logger.info(
                f"User {user.technical_id} activation processed successfully"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error processing user activation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_reactivation_notification(self, user: User) -> None:
        """Send reactivation notification to user"""
        try:
            # Placeholder for reactivation notification
            self.logger.info(f"Sent reactivation notification to {user.email}")

        except Exception as e:
            self.logger.warning(f"Failed to send reactivation notification: {str(e)}")
            # Don't raise - notification failure shouldn't stop activation
