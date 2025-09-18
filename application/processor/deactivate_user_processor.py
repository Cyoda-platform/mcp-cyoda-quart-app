"""
DeactivateUserProcessor for Cyoda Client Application

Handles the deactivation of User instances when they are deactivated.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.user.version_1.user import User


class DeactivateUserProcessor(CyodaProcessor):
    """
    Processor for deactivating User entities when they are deactivated.
    Sets deactivated date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DeactivateUserProcessor",
            description="Deactivates User instances by setting deactivated date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Deactivate the User entity according to functional requirements.

        Args:
            entity: The User entity to deactivate
            **kwargs: Additional processing parameters

        Returns:
            The deactivated user with deactivated date set
        """
        try:
            self.logger.info(
                f"Deactivating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Set deactivated date and update timestamp
            user.set_deactivated_date()

            self.logger.info(
                f"User {user.technical_id} deactivated successfully"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error deactivating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
