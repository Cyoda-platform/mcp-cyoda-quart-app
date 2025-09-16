"""
EggAlarmExpirationCriterion for Cyoda Client Application

Checks if an alarm notification has expired (not acknowledged within timeout period)
as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any

from application.entity.eggalarm.version_1.eggalarm import EggAlarm
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class EggAlarmExpirationCriterion(CyodaCriteriaChecker):
    """
    Expiration criterion for EggAlarm that checks if notification has expired.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmExpirationCriterion",
            description="Checks if EggAlarm notification has expired",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the alarm notification has expired.

        Args:
            entity: The CyodaEntity to check (expected to be EggAlarm)
            **kwargs: Additional criteria parameters

        Returns:
            True if the notification has expired, False otherwise
        """
        try:
            self.logger.info(
                f"Checking expiration for EggAlarm {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Check if alarm is active
            if not egg_alarm.isActive:
                self.logger.warning(f"EggAlarm {egg_alarm.technical_id} is not active")
                return False

            # Check if scheduled time is set
            if not egg_alarm.scheduledTime:
                self.logger.warning(
                    f"EggAlarm {egg_alarm.technical_id} has no scheduled time"
                )
                return False

            # Check if notification has expired (5 minutes after scheduled time)
            current_time = datetime.now(timezone.utc)
            scheduled_time = datetime.fromisoformat(
                egg_alarm.scheduledTime.replace("Z", "+00:00")
            )

            notification_timeout = 300  # 5 minutes in seconds
            expiration_time = scheduled_time.timestamp() + notification_timeout

            if current_time.timestamp() >= expiration_time:
                self.logger.info(
                    f"Notification has expired for EggAlarm {egg_alarm.technical_id}"
                )
                return True
            else:
                remaining_seconds = expiration_time - current_time.timestamp()
                self.logger.info(
                    f"Notification has not expired for EggAlarm {egg_alarm.technical_id} "
                    f"({remaining_seconds:.1f} seconds until expiration)"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Error checking expiration for EggAlarm {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
