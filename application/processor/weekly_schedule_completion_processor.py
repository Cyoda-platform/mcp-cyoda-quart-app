"""
WeeklyScheduleCompletionProcessor for Cyoda Client Application

Completes weekly cycle and generates reports.
"""

import logging
from typing import Any, cast

from application.entity.weeklyschedule.version_1.weeklyschedule import WeeklySchedule
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class WeeklyScheduleCompletionProcessor(CyodaProcessor):
    """Processor for completing weekly schedules and generating reports."""

    def __init__(self) -> None:
        super().__init__(
            name="WeeklyScheduleCompletionProcessor",
            description="Completes weekly cycle and generates reports",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process weekly schedule completion."""
        try:
            weekly_schedule = cast_entity(entity, WeeklySchedule)

            if weekly_schedule.state != "emails_sent":
                raise ValueError(
                    f"Weekly schedule must be in emails_sent state, current: {weekly_schedule.state}"
                )

            # Generate weekly report
            await self._generate_weekly_report(weekly_schedule)

            # Update timestamp
            weekly_schedule.update_timestamp()

            # Schedule next week's schedule creation (simulated)
            await self._schedule_next_week(weekly_schedule)

            self.logger.info(
                f"Weekly schedule completed for week {weekly_schedule.week_start_date}"
            )
            return weekly_schedule

        except Exception as e:
            self.logger.error(f"Error completing weekly schedule: {str(e)}")
            raise

    async def _generate_weekly_report(self, weekly_schedule: WeeklySchedule) -> None:
        """Generate weekly report."""
        try:
            success_rate = weekly_schedule.calculate_success_rate()

            report = {
                "week": weekly_schedule.week_start_date,
                "totalSubscribers": weekly_schedule.total_subscribers,
                "emailsSent": weekly_schedule.emails_sent,
                "emailsFailed": weekly_schedule.emails_failed,
                "successRate": success_rate,
            }

            # In a real implementation, this would save to database or send to administrators
            self.logger.info(f"Weekly report generated: {report}")

        except Exception as e:
            self.logger.error(f"Error generating weekly report: {str(e)}")

    async def _schedule_next_week(self, weekly_schedule: WeeklySchedule) -> None:
        """Schedule next week's schedule creation."""
        try:
            # In a real implementation, this would schedule a job for next week
            self.logger.info(
                f"Next week's schedule creation scheduled after {weekly_schedule.week_end_date}"
            )

        except Exception as e:
            self.logger.error(f"Error scheduling next week: {str(e)}")
