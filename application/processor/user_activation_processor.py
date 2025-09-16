"""
UserActivationProcessor for Cyoda Client Application

Activates a registered user account as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.user.version_1.user import User


class UserActivationProcessor(CyodaProcessor):
    """
    Processor for activating registered User entities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserActivationProcessor",
            description="Activates registered User entities after verification",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User activation according to functional requirements.

        Args:
            entity: The User entity to activate (should be in REGISTERED state)
            **kwargs: Additional processing parameters

        Returns:
            The activated user entity
        """
        try:
            self.logger.info(
                f"Processing User activation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Update timestamp
            user.update_timestamp()

            # Send welcome email
            await self._send_welcome_email(user.email)

            self.logger.info(f"User {user.technical_id} activated successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error processing User activation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_welcome_email(self, email: str) -> None:
        """
        Send welcome email to activated user.

        Args:
            email: The user's email address
        """
        try:
            # In a real implementation, this would send actual welcome email
            self.logger.info(f"Sending welcome email to {email}")
            
            # Could integrate with email service like SendGrid, AWS SES, etc.
            
        except Exception as e:
            self.logger.error(f"Failed to send welcome email to {email}: {str(e)}")
            # Don't raise - email failure shouldn't prevent activation
