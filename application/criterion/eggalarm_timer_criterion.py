"""
EggAlarmTimerCriterion for Cyoda Client Application

Checks if the alarm timer has elapsed and the alarm should be completed
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.eggalarm.version_1.eggalarm import EggAlarm


class EggAlarmTimerCriterion(CyodaCriteriaChecker):
    """
    Timer criterion for EggAlarm that checks if the timer has elapsed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmTimerCriterion",
            description="Checks if EggAlarm timer has elapsed for completion",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the alarm timer has elapsed.

        Args:
            entity: The CyodaEntity to check (expected to be EggAlarm)
            **kwargs: Additional criteria parameters

        Returns:
            True if the timer has elapsed, False otherwise
        """
        try:
            self.logger.info(f"Checking timer for EggAlarm {getattr(entity, 'technical_id', '<unknown>')}")

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Check if alarm is active
            if not egg_alarm.isActive:
                self.logger.warning(f"EggAlarm {egg_alarm.technical_id} is not active")
                return False

            # Check if scheduled time is set
            if not egg_alarm.scheduledTime:
                self.logger.warning(f"EggAlarm {egg_alarm.technical_id} has no scheduled time")
                return False

            # Check if timer has elapsed
            current_time = datetime.now(timezone.utc)
            scheduled_time = datetime.fromisoformat(egg_alarm.scheduledTime.replace("Z", "+00:00"))
            
            if current_time >= scheduled_time:
                self.logger.info(f"Timer has elapsed for EggAlarm {egg_alarm.technical_id}")
                return True
            else:
                remaining_seconds = (scheduled_time - current_time).total_seconds()
                self.logger.info(
                    f"Timer has not elapsed for EggAlarm {egg_alarm.technical_id} "
                    f"({remaining_seconds:.1f} seconds remaining)"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Error checking timer for EggAlarm {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
