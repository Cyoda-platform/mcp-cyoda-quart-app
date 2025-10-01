"""
CreateUserProcessor for Cyoda Client Application

Handles the creation of new user accounts with default settings
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CreateUserProcessor(CyodaProcessor):
    """
    Processor for creating new User accounts with default settings.
    Initializes user account in pending state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreateUserProcessor",
            description="Creates new user account with default settings and pending status",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User creation according to functional requirements.

        Args:
            entity: The User entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed user with pending status
        """
        try:
            self.logger.info(
                f"Creating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Set default values for new user
            user.is_active = False  # Users start inactive until activated
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Update timestamps
            if not user.created_at:
                user.created_at = current_timestamp
            user.updated_at = current_timestamp

            # Initialize role_ids if not set
            if user.role_ids is None:
                user.role_ids = []

            # Log user creation
            self.logger.info(
                f"User {user.username} created successfully with email {user.email}"
            )

            # Note: In a real implementation, you would:
            # - Send activation email to user.email
            # - Generate activation token
            # - Store activation token for later verification

            return user

        except Exception as e:
            self.logger.error(
                f"Error creating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
