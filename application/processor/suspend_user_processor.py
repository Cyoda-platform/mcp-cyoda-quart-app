"""
SuspendUserProcessor for Cyoda Client Application

Handles the temporary suspension of user accounts
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.user.version_1.user import User


class SuspendUserProcessor(CyodaProcessor):
    """
    Processor for temporarily suspending User accounts.
    Transitions user from active to suspended state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SuspendUserProcessor",
            description="Temporarily suspends user account access",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User suspension according to functional requirements.

        Args:
            entity: The User entity to suspend
            **kwargs: Additional processing parameters

        Returns:
            The suspended user
        """
        try:
            self.logger.info(
                f"Suspending User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Suspend the user account
            user.is_active = False
            current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            user.updated_at = current_timestamp

            # Add suspension metadata
            user.add_metadata("suspended_at", current_timestamp)
            user.add_metadata("suspension_reason", kwargs.get("reason", "Manual suspension"))

            # Log user suspension
            self.logger.info(
                f"User {user.username} suspended successfully"
            )

            # Note: In a real implementation, you would:
            # - Revoke all active sessions for this user
            # - Send notification email about suspension
            # - Log suspension event for audit trail
            # - Invalidate any active tokens

            return user

        except Exception as e:
            self.logger.error(
                f"Error suspending user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
