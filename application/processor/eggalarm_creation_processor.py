"""
EggAlarmCreationProcessor for Cyoda Client Application

Creates a new egg alarm with the specified parameters and calculates the cooking
duration based on egg type as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.eggalarm.version_1.eggalarm import EggAlarm
from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class EggAlarmCreationProcessor(CyodaProcessor):
    """
    Processor for creating EggAlarm entities with proper validation and
    duration calculation based on egg type.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EggAlarmCreationProcessor",
            description="Creates new EggAlarm entities with calculated duration and scheduled time",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EggAlarm creation according to functional requirements.

        Args:
            entity: The EggAlarm entity to process (should be in initial state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with calculated duration and scheduled time
        """
        try:
            self.logger.info(
                f"Processing EggAlarm creation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EggAlarm for type-safe operations
            egg_alarm = cast_entity(entity, EggAlarm)

            # Validate that user exists and is active
            await self._validate_user(egg_alarm.userId)

            # Set duration based on egg type if not already set
            if not hasattr(egg_alarm, "duration") or egg_alarm.duration == 0:
                egg_alarm.duration = self._get_duration_for_egg_type(egg_alarm.eggType)

            # Set creation time
            current_time = datetime.now(timezone.utc)
            egg_alarm.createdAt = current_time.isoformat().replace("+00:00", "Z")

            # Calculate scheduled time (creation time + duration)
            scheduled_timestamp = current_time.timestamp() + egg_alarm.duration
            egg_alarm.scheduledTime = (
                datetime.fromtimestamp(scheduled_timestamp, timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )

            # Set default title if not provided
            egg_alarm.ensure_title()

            # Set initial state
            egg_alarm.isActive = False

            self.logger.info(f"EggAlarm {egg_alarm.technical_id} created successfully")

            return egg_alarm

        except Exception as e:
            self.logger.error(
                f"Error processing EggAlarm creation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_user(self, user_id: str) -> None:
        """
        Validate that the user exists and is in ACTIVE state.

        Args:
            user_id: The user ID to validate
        """
        entity_service = get_entity_service()

        try:
            user_response = await entity_service.get_by_id(
                entity_id=user_id,
                entity_class=User.ENTITY_NAME,
                entity_version=str(User.ENTITY_VERSION),
            )

            if not user_response:
                raise ValueError(f"User {user_id} not found")

            user = cast_entity(user_response.data, User)
            if user.state != "ACTIVE":
                raise ValueError(f"User {user_id} must be in ACTIVE state")

        except Exception as e:
            self.logger.error(f"User validation failed for {user_id}: {str(e)}")
            raise

    def _get_duration_for_egg_type(self, egg_type: str) -> int:
        """
        Get cooking duration based on egg type.

        Args:
            egg_type: The type of egg cooking

        Returns:
            Duration in seconds
        """
        durations = {
            "SOFT_BOILED": 180,  # 3 minutes
            "MEDIUM_BOILED": 240,  # 4 minutes
            "HARD_BOILED": 360,  # 6 minutes
        }

        if egg_type not in durations:
            raise ValueError(f"Invalid egg type: {egg_type}")

        return durations[egg_type]
