"""
UserReactivationProcessor for Cyoda Client Application

Reactivates a suspended user account as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.user.version_1.user import User


class UserReactivationProcessor(CyodaProcessor):
    """
    Processor for reactivating suspended User entities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserReactivationProcessor",
            description="Reactivates suspended User entities",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User reactivation according to functional requirements.

        Args:
            entity: The User entity to reactivate (should be in SUSPENDED state)
            **kwargs: Additional processing parameters

        Returns:
            The reactivated user entity
        """
        try:
            self.logger.info(
                f"Processing User reactivation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Send reactivation notification
            await self._send_reactivation_notification(user.email)

            # Update timestamp
            user.update_timestamp()

            self.logger.info(f"User {user.technical_id} reactivated successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error processing User reactivation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_reactivation_notification(self, email: str) -> None:
        """
        Send reactivation notification to user.

        Args:
            email: The user's email address
        """
        try:
            # In a real implementation, this would send actual reactivation notification
            self.logger.info(f"Sending reactivation notification to {email}")
            
            # Could integrate with email service like SendGrid, AWS SES, etc.
            
        except Exception as e:
            self.logger.error(f"Failed to send reactivation notification to {email}: {str(e)}")
            # Don't raise - email failure shouldn't prevent reactivation
