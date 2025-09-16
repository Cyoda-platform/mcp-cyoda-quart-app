"""
EggAlarmCancellationProcessor for Cyoda Client Application

Cancels an active or created alarm as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.eggalarm.version_1.eggalarm import EggAlarm


class EggAlarmCancellationProcessor(CyodaProcessor):
    """
    Processor for cancelling EggAlarm entities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmCancellationProcessor",
            description="Cancels EggAlarm entities and stops timers",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EggAlarm cancellation according to functional requirements.

        Args:
            entity: The EggAlarm entity to cancel (can be in CREATED or ACTIVE state)
            **kwargs: Additional processing parameters

        Returns:
            The cancelled entity with deactivated status
        """
        try:
            self.logger.info(
                f"Processing EggAlarm cancellation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Stop timer if alarm was active
            if egg_alarm.isActive:
                self._stop_timer(egg_alarm.technical_id or egg_alarm.entity_id or "unknown")

            # Deactivate the alarm
            egg_alarm.deactivate()

            self.logger.info(f"EggAlarm {egg_alarm.technical_id} cancelled successfully")

            return egg_alarm

        except Exception as e:
            self.logger.error(
                f"Error processing EggAlarm cancellation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _stop_timer(self, alarm_id: str) -> None:
        """
        Stop the timer for the alarm (placeholder implementation).

        Args:
            alarm_id: The alarm ID
        """
        try:
            # In a real implementation, this would stop actual timer/scheduler
            self.logger.info(f"Stopping timer for alarm {alarm_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to stop timer for alarm {alarm_id}: {str(e)}")
            # Don't raise - timer stop failure shouldn't prevent cancellation
