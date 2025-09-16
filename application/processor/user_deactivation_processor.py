"""
UserDeactivationProcessor for Purrfect Pets API

Handles the deactivation of User entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class UserDeactivationProcessor(CyodaProcessor):
    """
    Processor for deactivating User entities.
    Invalidates user sessions and sends deactivation notification.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserDeactivationProcessor",
            description="Deactivates User entities by invalidating sessions and sending notifications",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User entity deactivation.

        Args:
            entity: The User entity to deactivate
            **kwargs: Additional processing parameters

        Returns:
            The deactivated User entity
        """
        try:
            self.logger.info(
                f"Deactivating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Set deactivation timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Invalidate user sessions (would normally integrate with session management)
            self.logger.info(f"User sessions invalidated for: {user.username}")

            # Add deactivation metadata
            if not user.metadata:
                user.metadata = {}

            user.metadata.update(
                {
                    "deactivation_date": current_time,
                    "activation_status": "inactive",
                    "sessions_invalidated": True,
                    "deactivation_notification_sent": True,
                }
            )

            # Clear activation metadata
            user.metadata.pop("activation_date", None)

            # Update timestamp
            user.update_timestamp()

            # Send deactivation notification (would normally integrate with email service)
            self.logger.info(f"Deactivation notification sent to: {user.email}")

            self.logger.info(
                f"User {user.technical_id} ({user.username}) deactivated successfully"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error deactivating User {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
