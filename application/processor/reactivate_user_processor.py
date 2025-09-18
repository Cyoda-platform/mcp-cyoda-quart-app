"""
ReactivateUserProcessor for Cyoda Client Application

Handles the reactivation of User instances when they are reactivated from inactive state.
"""

import logging
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReactivateUserProcessor(CyodaProcessor):
    """
    Processor for reactivating User entities when they are reactivated from inactive state.
    Clears deactivated date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReactivateUserProcessor",
            description="Reactivates User instances by clearing deactivated date and updating timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Reactivate the User entity according to functional requirements.

        Args:
            entity: The User entity to reactivate
            **kwargs: Additional processing parameters

        Returns:
            The reactivated user with deactivated date cleared
        """
        try:
            self.logger.info(
                f"Reactivating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Clear deactivated date and update timestamp
            user.clear_deactivated_date()

            self.logger.info(f"User {user.technical_id} reactivated successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error reactivating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
