"""
EggAlarmExpirationProcessor for Cyoda Client Application

Marks an alarm as expired when notification timeout is reached
as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.eggalarm.version_1.eggalarm import EggAlarm


class EggAlarmExpirationProcessor(CyodaProcessor):
    """
    Processor for expiring EggAlarm entities when notification timeout is reached.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmExpirationProcessor",
            description="Expires EggAlarm entities when notification timeout is reached",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EggAlarm expiration according to functional requirements.

        Args:
            entity: The EggAlarm entity to expire (should be in ACTIVE state)
            **kwargs: Additional processing parameters

        Returns:
            The expired entity with deactivated status
        """
        try:
            self.logger.info(
                f"Processing EggAlarm expiration {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Deactivate the alarm
            egg_alarm.deactivate()

            # Stop alarm sound if playing
            self._stop_alarm_sound()

            self.logger.info(f"EggAlarm {egg_alarm.technical_id} expired successfully")

            return egg_alarm

        except Exception as e:
            self.logger.error(
                f"Error processing EggAlarm expiration {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _stop_alarm_sound(self) -> None:
        """
        Stop alarm sound (placeholder implementation).
        """
        try:
            # In a real implementation, this would stop actual sound playback
            self.logger.info("Stopping alarm sound")
            
        except Exception as e:
            self.logger.error(f"Failed to stop alarm sound: {str(e)}")
            # Don't raise - sound stop failure shouldn't prevent expiration
