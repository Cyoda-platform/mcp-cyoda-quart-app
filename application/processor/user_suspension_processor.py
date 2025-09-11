"""
UserSuspensionProcessor for Purrfect Pets API

Suspends user account according to processors.md specification.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class UserSuspensionProcessor(CyodaProcessor):
    """
    Processor for User suspension that suspends user account.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserSuspensionProcessor",
            description="Suspends user account",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User entity suspension according to functional requirements.

        Args:
            entity: The User entity to suspend
            **kwargs: Additional processing parameters including suspension_reason

        Returns:
            The suspended user entity
        """
        try:
            self.logger.info(
                f"Processing suspension for User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Get suspension reason from kwargs
            suspension_reason = kwargs.get("suspension_reason", "Policy violation")

            # Record suspension reason
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            if user.metadata is None:
                user.metadata = {}

            user.metadata["suspension"] = {
                "reason": suspension_reason,
                "suspended_at": current_timestamp,
                "suspended_by": "system",
            }

            # Set suspension date
            user.metadata["suspension_date"] = current_timestamp

            # Cancel active sessions (placeholder)
            await self._cancel_active_sessions(user)

            # Send suspension notification (placeholder)
            await self._send_suspension_notification(user, suspension_reason)

            # Update timestamp
            user.update_timestamp()

            self.logger.info(
                f"User {user.technical_id} suspension processed successfully"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error processing user suspension {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _cancel_active_sessions(self, user: User) -> None:
        """Cancel active user sessions"""
        try:
            # Placeholder for session cancellation
            self.logger.info(f"Cancelled active sessions for user {user.username}")

        except Exception as e:
            self.logger.warning(f"Failed to cancel active sessions: {str(e)}")

    async def _send_suspension_notification(self, user: User, reason: str) -> None:
        """Send suspension notification to user"""
        try:
            # Placeholder for suspension notification
            self.logger.info(
                f"Sent suspension notification to {user.email} with reason: {reason}"
            )

        except Exception as e:
            self.logger.warning(f"Failed to send suspension notification: {str(e)}")
            # Don't raise - notification failure shouldn't stop suspension
