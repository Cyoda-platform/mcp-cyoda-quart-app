"""
RegisterUserProcessor for Cyoda Client Application

Handles the registration of User instances when they are first created.
"""

import logging
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class RegisterUserProcessor(CyodaProcessor):
    """
    Processor for registering User entities when they are first created.
    Sets registered date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RegisterUserProcessor",
            description="Registers User instances with registered date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Register the User entity according to functional requirements.

        Args:
            entity: The User entity to register
            **kwargs: Additional processing parameters

        Returns:
            The registered user with registered date set
        """
        try:
            self.logger.info(
                f"Registering User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Set registered date and update timestamp
            user.set_registered_date()

            self.logger.info(f"User {user.technical_id} registered successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error registering user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
