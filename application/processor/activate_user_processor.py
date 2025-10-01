"""
ActivateUserProcessor for Cyoda Client Application

Handles the activation of user accounts for login access
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.user.version_1.user import User


class ActivateUserProcessor(CyodaProcessor):
    """
    Processor for activating User accounts for login access.
    Transitions user from pending to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ActivateUserProcessor",
            description="Activates user account for login access",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User activation according to functional requirements.

        Args:
            entity: The User entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated user
        """
        try:
            self.logger.info(
                f"Activating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Activate the user account
            user.is_active = True
            current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            user.updated_at = current_timestamp

            # Add activation metadata
            user.add_metadata("activated_at", current_timestamp)
            user.add_metadata("activation_method", "manual")

            # Log user activation
            self.logger.info(
                f"User {user.username} activated successfully"
            )

            # Note: In a real implementation, you would:
            # - Send welcome email to user.email
            # - Log activation event for audit trail
            # - Initialize user preferences/settings

            return user

        except Exception as e:
            self.logger.error(
                f"Error activating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
