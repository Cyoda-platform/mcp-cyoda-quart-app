"""
EggAlarmActivationProcessor for Cyoda Client Application

Activates the egg alarm and starts the countdown timer as specified 
in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.eggalarm.version_1.eggalarm import EggAlarm


class EggAlarmActivationProcessor(CyodaProcessor):
    """
    Processor for activating EggAlarm entities and starting the countdown timer.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmActivationProcessor",
            description="Activates EggAlarm entities and starts countdown timer",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EggAlarm activation according to functional requirements.

        Args:
            entity: The EggAlarm entity to activate (should be in CREATED state)
            **kwargs: Additional processing parameters

        Returns:
            The activated entity with updated scheduled time and active status
        """
        try:
            self.logger.info(
                f"Processing EggAlarm activation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Set alarm as active
            egg_alarm.isActive = True

            # Recalculate scheduled time from current time
            current_time = datetime.now(timezone.utc)
            scheduled_timestamp = current_time.timestamp() + egg_alarm.duration
            egg_alarm.scheduledTime = datetime.fromtimestamp(
                scheduled_timestamp, timezone.utc
            ).isoformat().replace("+00:00", "Z")

            # Update timestamp
            egg_alarm.update_timestamp()

            # Log timer start (in real implementation, this would start actual timer)
            self.logger.info(
                f"Started timer for EggAlarm {egg_alarm.technical_id} - "
                f"duration: {egg_alarm.duration}s, scheduled: {egg_alarm.scheduledTime}"
            )

            self.logger.info(f"EggAlarm {egg_alarm.technical_id} activated successfully")

            return egg_alarm

        except Exception as e:
            self.logger.error(
                f"Error processing EggAlarm activation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
