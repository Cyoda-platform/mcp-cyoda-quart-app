"""
WeeklySchedule Time Criterion for checking if it's time to retrieve cat fact for weekly distribution.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.weeklyschedule.version_1.weeklyschedule import \
    WeeklySchedule
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class WeeklyScheduleTimeCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if it's time to retrieve cat fact for weekly distribution."""

    def __init__(
        self, name: str = "WeeklyScheduleTimeCriterion", description: str = ""
    ):
        super().__init__(
            name=name,
            description=description
            or "Checks if it's time to retrieve cat fact for weekly distribution",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if it's time to execute weekly schedule."""
        try:
            if not isinstance(entity, WeeklySchedule):
                return False

            # Check if scheduled date is set
            if not entity.scheduledDate:
                return False

            # Get current time
            current_time = datetime.now(timezone.utc)

            # Parse scheduled date
            scheduled_time = entity.scheduledDate
            if isinstance(scheduled_time, str):
                try:
                    scheduled_time = datetime.fromisoformat(
                        scheduled_time.replace("Z", "+00:00")
                    )
                except ValueError:
                    logger.error(f"Invalid scheduledDate format: {scheduled_time}")
                    return False

            # Check if current time is at or after scheduled time
            return current_time >= scheduled_time

        except Exception as e:
            logger.exception(
                f"Failed to check time criteria for weekly schedule {entity.entity_id}"
            )
            raise CriteriaError(
                self.name, f"Failed to check time criteria: {str(e)}", e
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, WeeklySchedule)
