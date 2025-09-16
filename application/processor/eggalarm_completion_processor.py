"""
EggAlarmCompletionProcessor for Cyoda Client Application

Completes the alarm when the timer expires and sends notification to the user
as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.eggalarm.version_1.eggalarm import EggAlarm
from application.entity.user.version_1.user import User
from services.services import get_entity_service


class EggAlarmCompletionProcessor(CyodaProcessor):
    """
    Processor for completing EggAlarm entities when timer expires.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmCompletionProcessor",
            description="Completes EggAlarm entities and sends notifications",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EggAlarm completion according to functional requirements.

        Args:
            entity: The EggAlarm entity to complete (should be in ACTIVE state)
            **kwargs: Additional processing parameters

        Returns:
            The completed entity with deactivated status
        """
        try:
            self.logger.info(
                f"Processing EggAlarm completion {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Deactivate the alarm
            egg_alarm.deactivate()

            # Get user for notification
            user = await self._get_user(egg_alarm.userId)

            # Send notification to user
            await self._send_notification(user, egg_alarm)

            # Play alarm sound (placeholder)
            self._play_alarm_sound()

            self.logger.info(f"EggAlarm {egg_alarm.technical_id} completed successfully")

            return egg_alarm

        except Exception as e:
            self.logger.error(
                f"Error processing EggAlarm completion {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_user(self, user_id: str) -> User:
        """
        Get the user entity for notification.

        Args:
            user_id: The user ID

        Returns:
            The User entity
        """
        entity_service = get_entity_service()
        
        try:
            user_response = await entity_service.get_by_id(
                entity_id=user_id,
                entity_class=User.ENTITY_NAME,
                entity_version=str(User.ENTITY_VERSION),
            )
            
            if not user_response:
                raise ValueError(f"User {user_id} not found")
            
            return cast_entity(user_response.data, User)
                
        except Exception as e:
            self.logger.error(f"Failed to get user {user_id}: {str(e)}")
            raise

    async def _send_notification(self, user: User, egg_alarm: EggAlarm) -> None:
        """
        Send notification to user about alarm completion.

        Args:
            user: The User entity
            egg_alarm: The completed EggAlarm entity
        """
        try:
            notification_message = f"Your {egg_alarm.eggType.replace('_', ' ').lower()} eggs are ready!"
            
            # In a real implementation, this would send actual notifications
            # For now, we'll just log the notification
            self.logger.info(
                f"Sending notification to user {user.username} ({user.email}): {notification_message}"
            )
            
            # Could integrate with email service, push notifications, etc.
            
        except Exception as e:
            self.logger.error(f"Failed to send notification to user {user.username}: {str(e)}")
            # Don't raise - notification failure shouldn't prevent alarm completion

    def _play_alarm_sound(self) -> None:
        """
        Play alarm sound (placeholder implementation).
        """
        try:
            # In a real implementation, this would trigger actual sound playback
            self.logger.info("Playing alarm sound")
            
        except Exception as e:
            self.logger.error(f"Failed to play alarm sound: {str(e)}")
            # Don't raise - sound failure shouldn't prevent alarm completion
