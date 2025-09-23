"""
EggAlarmCompletionProcessor for Cyoda Client Application

Handles the completion logic for EggAlarm instances when they transition
from active to completed state. Finalizes alarm data and logs completion.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.egg_alarm.version_1.egg_alarm import EggAlarm


class EggAlarmCompletionProcessor(CyodaProcessor):
    """
    Processor for EggAlarm that handles completion logic and finalization.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmCompletionProcessor",
            description="Processes EggAlarm completion and finalization",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EggAlarm for completion.

        Args:
            entity: The EggAlarm to process (must be in 'active' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with completion data
        """
        try:
            self.logger.info(
                f"Processing EggAlarm completion for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Create completion data
            completion_data = self._create_completion_data(egg_alarm)
            egg_alarm.completion_data = completion_data

            # Update status and timestamp
            egg_alarm.status = egg_alarm.status.__class__.COMPLETED
            egg_alarm.update_timestamp()

            # Log completion with cooking details
            self.logger.info(
                f"EggAlarm {egg_alarm.technical_id} completed successfully - "
                f"{egg_alarm.egg_type.value} egg cooked for {egg_alarm.get_cooking_time_display()}"
            )

            return egg_alarm

        except Exception as e:
            self.logger.error(
                f"Error processing EggAlarm completion {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_completion_data(self, entity: EggAlarm) -> Dict[str, Any]:
        """
        Create completion data for the EggAlarm.

        Args:
            entity: The EggAlarm to create completion data for

        Returns:
            Dictionary containing completion data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        completion_id = str(uuid.uuid4())

        # Calculate actual cooking time if we have scheduling data
        actual_cooking_time = None
        if entity.scheduled_data and "scheduled_at" in entity.scheduled_data:
            try:
                scheduled_at = datetime.fromisoformat(
                    entity.scheduled_data["scheduled_at"].replace("Z", "+00:00")
                )
                completed_at = datetime.now(timezone.utc)
                actual_cooking_time = int((completed_at - scheduled_at).total_seconds() / 60)
            except (ValueError, KeyError):
                # Fallback to expected cooking time
                actual_cooking_time = entity.cooking_duration

        completion_data: Dict[str, Any] = {
            "completed_at": current_timestamp,
            "completion_id": completion_id,
            "egg_type": entity.egg_type.value,
            "expected_cooking_duration": entity.cooking_duration,
            "actual_cooking_time_minutes": actual_cooking_time or entity.cooking_duration,
            "completion_status": "SUCCESS",
            "created_by": entity.created_by,
            "completion_message": f"Your {entity.egg_type.value} egg is ready! Cooked for {entity.get_cooking_time_display()}.",
        }

        # Include scheduling data reference if available
        if entity.scheduled_data and "scheduling_id" in entity.scheduled_data:
            completion_data["scheduling_id"] = entity.scheduled_data["scheduling_id"]

        return completion_data
