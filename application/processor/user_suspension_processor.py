"""
UserSuspensionProcessor for Cyoda Client Application

Suspends an active user account as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.eggalarm.version_1.eggalarm import EggAlarm
from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class UserSuspensionProcessor(CyodaProcessor):
    """
    Processor for suspending active User entities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserSuspensionProcessor",
            description="Suspends active User entities and cancels their alarms",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User suspension according to functional requirements.

        Args:
            entity: The User entity to suspend (should be in ACTIVE state)
            **kwargs: Additional processing parameters (should include reason)

        Returns:
            The suspended user entity
        """
        try:
            self.logger.info(
                f"Processing User suspension {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Get suspension reason from kwargs
            reason = kwargs.get("reason", "Policy violation")

            # Cancel all active alarms for this user
            await self._cancel_all_active_alarms(
                user.technical_id or user.entity_id or "unknown"
            )

            # Send suspension notification
            await self._send_suspension_notification(user.email, reason)

            # Update timestamp
            user.update_timestamp()

            self.logger.info(f"User {user.technical_id} suspended successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error processing User suspension {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _cancel_all_active_alarms(self, user_id: str) -> None:
        """
        Cancel all active alarms for the suspended user.

        Args:
            user_id: The user ID
        """
        try:
            entity_service = get_entity_service()

            # Find all alarms for this user
            # In a real implementation, we would search for alarms by userId
            # For now, we'll just log the action
            self.logger.info(f"Cancelling all active alarms for user {user_id}")

            # This would involve:
            # 1. Search for all EggAlarms with userId = user_id and state = ACTIVE
            # 2. For each alarm, trigger cancellation transition

        except Exception as e:
            self.logger.error(f"Failed to cancel alarms for user {user_id}: {str(e)}")
            # Don't raise - alarm cancellation failure shouldn't prevent suspension

    async def _send_suspension_notification(self, email: str, reason: str) -> None:
        """
        Send suspension notification to user.

        Args:
            email: The user's email address
            reason: The suspension reason
        """
        try:
            # In a real implementation, this would send actual suspension notification
            self.logger.info(
                f"Sending suspension notification to {email} - Reason: {reason}"
            )

            # Could integrate with email service like SendGrid, AWS SES, etc.

        except Exception as e:
            self.logger.error(
                f"Failed to send suspension notification to {email}: {str(e)}"
            )
            # Don't raise - email failure shouldn't prevent suspension
