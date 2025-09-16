"""
EggAlarmResetProcessor for Cyoda Client Application

Resets a completed alarm to create a new one with the same settings
as specified in functional requirements.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.eggalarm.version_1.eggalarm import EggAlarm


class EggAlarmResetProcessor(CyodaProcessor):
    """
    Processor for resetting completed EggAlarm entities to create new ones.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmResetProcessor",
            description="Resets completed EggAlarm entities with same settings",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EggAlarm reset according to functional requirements.

        Args:
            entity: The EggAlarm entity to reset (should be in COMPLETED state)
            **kwargs: Additional processing parameters

        Returns:
            A new EggAlarm entity with the same settings in CREATED state
        """
        try:
            self.logger.info(
                f"Processing EggAlarm reset {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            original_alarm = cast_entity(entity, EggAlarm)

            # Create new alarm with same settings
            current_time = datetime.now(timezone.utc)
            
            # Create new EggAlarm with same settings
            new_alarm = EggAlarm(
                entity_id=str(uuid.uuid4()),
                userId=original_alarm.userId,
                eggType=original_alarm.eggType,
                duration=original_alarm.duration,
                title=original_alarm.title,
                createdAt=current_time.isoformat().replace("+00:00", "Z"),
                scheduledTime=None,  # Will be set when activated
                isActive=False,
            )

            # Calculate scheduled time (creation time + duration)
            scheduled_timestamp = current_time.timestamp() + new_alarm.duration
            new_alarm.scheduledTime = datetime.fromtimestamp(
                scheduled_timestamp, timezone.utc
            ).isoformat().replace("+00:00", "Z")

            # Ensure title is set
            new_alarm.ensure_title()

            self.logger.info(
                f"EggAlarm reset successfully - new alarm {new_alarm.entity_id} created from {original_alarm.technical_id}"
            )

            return new_alarm

        except Exception as e:
            self.logger.error(
                f"Error processing EggAlarm reset {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
