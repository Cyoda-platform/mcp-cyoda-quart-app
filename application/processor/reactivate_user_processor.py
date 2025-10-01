"""
ReactivateUserProcessor for Cyoda Client Application

Handles the reactivation of suspended user accounts
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReactivateUserProcessor(CyodaProcessor):
    """
    Processor for reactivating suspended User accounts.
    Transitions user from suspended back to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReactivateUserProcessor",
            description="Reactivates suspended user account for login access",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User reactivation according to functional requirements.

        Args:
            entity: The User entity to reactivate
            **kwargs: Additional processing parameters

        Returns:
            The reactivated user
        """
        try:
            self.logger.info(
                f"Reactivating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Reactivate the user account
            user.is_active = True
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            user.updated_at = current_timestamp

            # Add reactivation metadata
            user.add_metadata("reactivated_at", current_timestamp)
            user.add_metadata(
                "reactivation_reason", kwargs.get("reason", "Manual reactivation")
            )

            # Clear suspension metadata
            if user.metadata and "suspended_at" in user.metadata:
                user.add_metadata(
                    "previous_suspension_cleared", user.metadata.get("suspended_at")
                )

            # Log user reactivation
            self.logger.info(f"User {user.username} reactivated successfully")

            # Note: In a real implementation, you would:
            # - Send reactivation notification email
            # - Log reactivation event for audit trail
            # - Reset any suspension-related flags
            # - Notify user of account restoration

            return user

        except Exception as e:
            self.logger.error(
                f"Error reactivating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
