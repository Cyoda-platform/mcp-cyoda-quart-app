"""
DeactivateUserProcessor for Cyoda Client Application

Handles the permanent deactivation of user accounts
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.user.version_1.user import User


class DeactivateUserProcessor(CyodaProcessor):
    """
    Processor for permanently deactivating User accounts.
    Transitions user from active to inactive state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DeactivateUserProcessor",
            description="Permanently deactivates user account",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User deactivation according to functional requirements.

        Args:
            entity: The User entity to deactivate
            **kwargs: Additional processing parameters

        Returns:
            The deactivated user
        """
        try:
            self.logger.info(
                f"Deactivating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Permanently deactivate the user account
            user.is_active = False
            current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            user.updated_at = current_timestamp

            # Add deactivation metadata
            user.add_metadata("deactivated_at", current_timestamp)
            user.add_metadata("deactivation_reason", kwargs.get("reason", "Manual deactivation"))
            user.add_metadata("deactivation_type", "permanent")

            # Clear role assignments for security
            if user.role_ids:
                user.add_metadata("previous_roles", user.role_ids.copy())
                user.role_ids = []

            # Log user deactivation
            self.logger.info(
                f"User {user.username} deactivated permanently"
            )

            # Note: In a real implementation, you would:
            # - Revoke all active sessions permanently
            # - Send account closure notification email
            # - Log deactivation event for audit trail
            # - Archive user data according to retention policy
            # - Remove from all active groups/roles
            # - Invalidate all tokens permanently

            return user

        except Exception as e:
            self.logger.error(
                f"Error deactivating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
