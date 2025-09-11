"""
WeeklyScheduleCreationProcessor for Cyoda Client Application

Creates new weekly schedule for cat fact distribution.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Protocol, cast

from application.entity.weeklyschedule.version_1.weeklyschedule import WeeklySchedule
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _EntityService(Protocol):
    async def search(
        self, entity_class: str, condition: Any, entity_version: str = "1"
    ) -> list[Any]: ...


class WeeklyScheduleCreationProcessor(CyodaProcessor):
    """Processor for creating new weekly schedules."""

    def __init__(self) -> None:
        super().__init__(
            name="WeeklyScheduleCreationProcessor",
            description="Creates new weekly schedule for cat fact distribution",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process weekly schedule creation."""
        try:
            weekly_schedule = cast_entity(entity, WeeklySchedule)

            # Validate week start date is Monday
            week_start_str = (
                kwargs.get("week_start_date") or weekly_schedule.week_start_date
            )
            week_start = datetime.strptime(week_start_str, "%Y-%m-%d")

            if week_start.weekday() != 0:
                raise ValueError("Week start date must be a Monday")

            # Validate no existing schedule for this week
            await self._validate_no_existing_schedule(week_start_str)

            # Set schedule fields
            weekly_schedule.week_start_date = week_start_str
            weekly_schedule.week_end_date = (week_start + timedelta(days=6)).strftime(
                "%Y-%m-%d"
            )
            weekly_schedule.scheduled_send_date = week_start_str  # Monday
            weekly_schedule.total_subscribers = await self._count_active_subscribers()
            weekly_schedule.emails_sent = 0
            weekly_schedule.emails_failed = 0

            weekly_schedule.update_timestamp()

            self.logger.info(f"Weekly schedule created for week {week_start_str}")
            return weekly_schedule

        except Exception as e:
            self.logger.error(f"Error creating weekly schedule: {str(e)}")
            raise

    async def _validate_no_existing_schedule(self, week_start_date: str) -> None:
        """Validate no existing schedule for this week."""
        entity_service = self._get_entity_service()

        try:
            existing = await entity_service.search(
                entity_class="WeeklySchedule",
                condition={"weekStartDate": week_start_date},
                entity_version="1",
            )

            if existing:
                raise ValueError("Schedule already exists for this week")

        except Exception as e:
            if "already exists" in str(e):
                raise
            self.logger.warning(f"Error checking existing schedules: {str(e)}")

    async def _count_active_subscribers(self) -> int:
        """Count active subscribers."""
        entity_service = self._get_entity_service()

        try:
            subscribers = await entity_service.search(
                entity_class="Subscriber",
                condition={"isActive": True, "state": "active"},
                entity_version="1",
            )
            return len(subscribers)
        except Exception as e:
            self.logger.warning(f"Error counting subscribers: {str(e)}")
            return 0
