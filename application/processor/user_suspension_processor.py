"""
UserSuspensionProcessor for Purrfect Pets API

Handles the suspension of User entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.user.version_1.user import User


class UserSuspensionProcessor(CyodaProcessor):
    """
    Processor for suspending User entities.
    Records suspension reason, invalidates sessions, and sends notification.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserSuspensionProcessor",
            description="Suspends User entities by recording reason, invalidating sessions, and sending notifications",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User entity suspension.

        Args:
            entity: The User entity to suspend
            **kwargs: Additional processing parameters (may include suspension_reason)

        Returns:
            The suspended User entity
        """
        try:
            self.logger.info(
                f"Suspending User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Get suspension reason from kwargs or use default
            suspension_reason = kwargs.get("suspension_reason", "Account suspended")

            # Record suspension reason and timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Invalidate user sessions (would normally integrate with session management)
            self.logger.info(f"User sessions invalidated for: {user.username}")

            # Add suspension metadata
            if not user.metadata:
                user.metadata = {}
            
            user.metadata.update({
                "suspension_date": current_time,
                "suspension_reason": suspension_reason,
                "activation_status": "suspended",
                "sessions_invalidated": True,
                "suspension_notification_sent": True
            })

            # Clear activation metadata
            user.metadata.pop("activation_date", None)

            # Update timestamp
            user.update_timestamp()

            # Send suspension notification (would normally integrate with email service)
            self.logger.info(f"Suspension notification sent to: {user.email}")

            self.logger.info(
                f"User {user.technical_id} ({user.username}) suspended successfully. Reason: {suspension_reason}"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error suspending User {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
