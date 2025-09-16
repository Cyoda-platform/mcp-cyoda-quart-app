"""
WeeklySchedule Completion Processor for completing weekly schedules.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from application.entity.weeklyschedule.version_1.weeklyschedule import \
    WeeklySchedule
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class WeeklyScheduleCompletionProcessor(CyodaProcessor):
    """Processor to complete weekly schedules."""

    def __init__(
        self, name: str = "WeeklyScheduleCompletionProcessor", description: str = ""
    ):
        super().__init__(
            name=name, description=description or "Completes weekly schedule"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Complete weekly schedule."""
        try:
            if not isinstance(entity, WeeklySchedule):
                raise ProcessorError(
                    self.name, f"Expected WeeklySchedule entity, got {type(entity)}"
                )

            # Set execution timestamp
            entity.executedDate = datetime.now(timezone.utc)

            # Add completion metadata
            entity.add_metadata("completed_at", entity.executedDate.isoformat())
            entity.add_metadata("completion_status", "success")

            # Schedule next week's WeeklySchedule creation
            # In a real implementation, this would be handled by a scheduler
            next_week_start = entity.weekStartDate + timedelta(days=7)
            entity.add_metadata("next_schedule_date", next_week_start.isoformat())

            logger.info(
                f"Completed weekly schedule {entity.id} for week {entity.weekStartDate}"
            )
            return entity

        except Exception as e:
            logger.exception(f"Failed to complete weekly schedule {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to complete weekly schedule: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, WeeklySchedule)
