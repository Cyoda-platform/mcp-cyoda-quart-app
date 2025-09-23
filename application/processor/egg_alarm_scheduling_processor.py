"""
EggAlarmSchedulingProcessor for Cyoda Client Application

Handles the scheduling logic for EggAlarm instances when they transition
from scheduled to active state. Sets up alarm timing and activation data.
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.egg_alarm.version_1.egg_alarm import EggAlarm


class EggAlarmSchedulingProcessor(CyodaProcessor):
    """
    Processor for EggAlarm that handles scheduling logic and activation setup.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmSchedulingProcessor",
            description="Processes EggAlarm scheduling and activation setup",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EggAlarm for scheduling and activation.

        Args:
            entity: The EggAlarm to process (must be in 'scheduled' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with scheduling data
        """
        try:
            self.logger.info(
                f"Processing EggAlarm scheduling for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Create scheduling data
            scheduling_data = self._create_scheduling_data(egg_alarm)
            egg_alarm.scheduled_data = scheduling_data

            # Set alarm time if not already set
            if not egg_alarm.alarm_time:
                # Set alarm time to current time + cooking duration
                alarm_time = datetime.now(timezone.utc) + timedelta(minutes=egg_alarm.cooking_duration)
                egg_alarm.alarm_time = alarm_time.isoformat().replace("+00:00", "Z")

            # Update status and timestamp
            egg_alarm.status = egg_alarm.status.__class__.ACTIVE
            egg_alarm.update_timestamp()

            self.logger.info(
                f"EggAlarm {egg_alarm.technical_id} scheduled successfully for {egg_alarm.get_cooking_time_display()}"
            )

            return egg_alarm

        except Exception as e:
            self.logger.error(
                f"Error processing EggAlarm scheduling {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_scheduling_data(self, entity: EggAlarm) -> Dict[str, Any]:
        """
        Create scheduling data for the EggAlarm.

        Args:
            entity: The EggAlarm to create scheduling data for

        Returns:
            Dictionary containing scheduling data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        scheduling_id = str(uuid.uuid4())

        # Calculate expected completion time
        if entity.alarm_time:
            try:
                alarm_dt = datetime.fromisoformat(entity.alarm_time.replace("Z", "+00:00"))
                expected_completion = alarm_dt.isoformat().replace("+00:00", "Z")
            except ValueError:
                # Fallback if alarm_time is invalid
                expected_completion = (
                    datetime.now(timezone.utc) + timedelta(minutes=entity.cooking_duration)
                ).isoformat().replace("+00:00", "Z")
        else:
            expected_completion = (
                datetime.now(timezone.utc) + timedelta(minutes=entity.cooking_duration)
            ).isoformat().replace("+00:00", "Z")

        scheduling_data: Dict[str, Any] = {
            "scheduled_at": current_timestamp,
            "scheduling_id": scheduling_id,
            "egg_type": entity.egg_type.value,
            "cooking_duration_minutes": entity.cooking_duration,
            "expected_completion": expected_completion,
            "scheduling_status": "ACTIVE",
            "created_by": entity.created_by,
        }

        return scheduling_data
