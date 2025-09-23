"""
EggAlarmValidationCriterion for Cyoda Client Application

Validates that an EggAlarm meets all required business rules before it can
proceed to the scheduling stage as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.egg_alarm.version_1.egg_alarm import EggAlarm, EggType


class EggAlarmValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for EggAlarm that checks all business rules
    before the entity can proceed to scheduling stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmValidationCriterion",
            description="Validates EggAlarm business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be EggAlarm)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating EggAlarm {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Validate required fields
            if not egg_alarm.created_by or len(egg_alarm.created_by.strip()) == 0:
                self.logger.warning(
                    f"EggAlarm {egg_alarm.technical_id} has invalid created_by field"
                )
                return False

            # Validate egg type
            if egg_alarm.egg_type not in EggType:
                self.logger.warning(
                    f"EggAlarm {egg_alarm.technical_id} has invalid egg_type: {egg_alarm.egg_type}"
                )
                return False

            # Validate cooking duration matches egg type
            expected_duration = EggAlarm.COOKING_DURATIONS.get(egg_alarm.egg_type)
            if expected_duration and egg_alarm.cooking_duration != expected_duration:
                self.logger.warning(
                    f"EggAlarm {egg_alarm.technical_id} has incorrect cooking duration: "
                    f"expected {expected_duration} for {egg_alarm.egg_type}, got {egg_alarm.cooking_duration}"
                )
                return False

            # Validate cooking duration range
            if egg_alarm.cooking_duration < 1 or egg_alarm.cooking_duration > 30:
                self.logger.warning(
                    f"EggAlarm {egg_alarm.technical_id} has invalid cooking duration: {egg_alarm.cooking_duration}"
                )
                return False

            # Validate alarm time format if provided
            if egg_alarm.alarm_time:
                try:
                    alarm_dt = datetime.fromisoformat(egg_alarm.alarm_time.replace("Z", "+00:00"))
                    # Check if alarm time is not in the past (with 1 minute tolerance)
                    current_time = datetime.now(timezone.utc)
                    if alarm_dt < current_time:
                        self.logger.warning(
                            f"EggAlarm {egg_alarm.technical_id} has alarm time in the past: {egg_alarm.alarm_time}"
                        )
                        return False
                except ValueError:
                    self.logger.warning(
                        f"EggAlarm {egg_alarm.technical_id} has invalid alarm time format: {egg_alarm.alarm_time}"
                    )
                    return False

            # Validate notes length if provided
            if egg_alarm.notes and len(egg_alarm.notes) > 500:
                self.logger.warning(
                    f"EggAlarm {egg_alarm.technical_id} has notes too long: {len(egg_alarm.notes)} characters"
                )
                return False

            # Validate created_by length
            if len(egg_alarm.created_by) > 100:
                self.logger.warning(
                    f"EggAlarm {egg_alarm.technical_id} has created_by too long: {len(egg_alarm.created_by)} characters"
                )
                return False

            # Business logic validation: ensure alarm is in correct status for scheduling
            if egg_alarm.status and egg_alarm.status.value not in ["pending", "scheduled"]:
                self.logger.warning(
                    f"EggAlarm {egg_alarm.technical_id} has invalid status for scheduling: {egg_alarm.status}"
                )
                return False

            self.logger.info(
                f"EggAlarm {egg_alarm.technical_id} passed all validation criteria - "
                f"{egg_alarm.egg_type.value} for {egg_alarm.get_cooking_time_display()}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating EggAlarm {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
