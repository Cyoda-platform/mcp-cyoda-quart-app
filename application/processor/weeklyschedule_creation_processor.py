"""
WeeklySchedule Creation Processor for creating weekly schedules.
"""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, Optional

from application.entity.weeklyschedule.version_1.weeklyschedule import \
    WeeklySchedule
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class WeeklyScheduleCreationProcessor(CyodaProcessor):
    """Processor to create weekly schedules for cat fact distribution."""

    def __init__(
        self, name: str = "WeeklyScheduleCreationProcessor", description: str = ""
    ):
        super().__init__(
            name=name,
            description=description
            or "Creates weekly schedule for cat fact distribution",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Create weekly schedule."""
        try:
            if not isinstance(entity, WeeklySchedule):
                raise ProcessorError(
                    self.name, f"Expected WeeklySchedule entity, got {type(entity)}"
                )

            # Calculate current week start and end dates
            now = datetime.now(timezone.utc)

            # If dates not provided, calculate them
            if not entity.weekStartDate:
                # Get Monday of current week
                days_since_monday = now.weekday()
                week_start = (now - timedelta(days=days_since_monday)).date()
                entity.weekStartDate = week_start

            if not entity.weekEndDate:
                # Get Sunday of current week
                entity.weekEndDate = entity.weekStartDate + timedelta(days=6)

            # Set scheduled date (next Monday 9 AM)
            if not entity.scheduledDate:
                next_monday = entity.weekStartDate + timedelta(days=7)
                entity.scheduledDate = datetime.combine(
                    next_monday, datetime.min.time().replace(hour=9)
                )
                entity.scheduledDate = entity.scheduledDate.replace(tzinfo=timezone.utc)

            # Count active subscribers
            entity_service = self._get_entity_service()
            subscribers = await entity_service.find_all("subscriber", "1")
            active_count = sum(
                1
                for sub in subscribers
                if sub.data.get("isActive") and sub.data.get("state") == "active"
            )
            entity.subscriberCount = active_count

            logger.info(
                f"Created weekly schedule for {entity.weekStartDate} with {active_count} subscribers"
            )
            return entity

        except Exception as e:
            logger.exception(f"Failed to create weekly schedule {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to create weekly schedule: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, WeeklySchedule)

    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service

        return get_entity_service()
