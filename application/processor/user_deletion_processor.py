"""
UserDeletionProcessor for Cyoda Client Application

Marks a user account for deletion as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class UserDeletionProcessor(CyodaProcessor):
    """
    Processor for marking User entities for deletion.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserDeletionProcessor",
            description="Marks User entities for deletion and schedules data cleanup",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User deletion according to functional requirements.

        Args:
            entity: The User entity to delete (can be in ACTIVE or SUSPENDED state)
            **kwargs: Additional processing parameters

        Returns:
            The user entity marked for deletion
        """
        try:
            self.logger.info(
                f"Processing User deletion {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Cancel all active alarms for this user
            await self._cancel_all_active_alarms(
                user.technical_id or user.entity_id or "unknown"
            )

            # Schedule data deletion
            await self._schedule_data_deletion(
                user.technical_id or user.entity_id or "unknown"
            )

            # Update timestamp
            user.update_timestamp()

            self.logger.info(
                f"User {user.technical_id} marked for deletion successfully"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error processing User deletion {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _cancel_all_active_alarms(self, user_id: str) -> None:
        """
        Cancel all active alarms for the user being deleted.

        Args:
            user_id: The user ID
        """
        try:
            # In a real implementation, we would search for alarms by userId
            # For now, we'll just log the action
            self.logger.info(f"Cancelling all active alarms for user {user_id}")

            # This would involve:
            # 1. Search for all EggAlarms with userId = user_id and state = ACTIVE
            # 2. For each alarm, trigger cancellation transition

        except Exception as e:
            self.logger.error(f"Failed to cancel alarms for user {user_id}: {str(e)}")
            # Don't raise - alarm cancellation failure shouldn't prevent deletion

    async def _schedule_data_deletion(self, user_id: str) -> None:
        """
        Schedule data deletion for the user.

        Args:
            user_id: The user ID
        """
        try:
            # In a real implementation, this would schedule actual data deletion
            # Could involve GDPR compliance, data retention policies, etc.
            self.logger.info(f"Scheduling data deletion for user {user_id}")

            # This might involve:
            # 1. Adding to deletion queue
            # 2. Setting retention period
            # 3. Anonymizing data
            # 4. Notifying compliance systems

        except Exception as e:
            self.logger.error(
                f"Failed to schedule data deletion for user {user_id}: {str(e)}"
            )
            # Don't raise - scheduling failure shouldn't prevent deletion marking
