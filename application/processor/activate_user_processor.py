"""
ActivateUserProcessor for Cyoda Client Application

Handles the activation of User instances when they are activated.
"""

import logging
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ActivateUserProcessor(CyodaProcessor):
    """
    Processor for activating User entities when they are activated.
    Sets activated date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ActivateUserProcessor",
            description="Activates User instances by setting activated date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Activate the User entity according to functional requirements.

        Args:
            entity: The User entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated user with activated date set
        """
        try:
            self.logger.info(
                f"Activating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Set activated date and update timestamp
            user.set_activated_date()

            self.logger.info(f"User {user.technical_id} activated successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error activating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
