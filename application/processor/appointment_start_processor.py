"""
Appointment Start Processor for Purrfect Pets API.
"""

import logging
from datetime import datetime, timezone

from application.entity.appointment.version_1.appointment import Appointment
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class AppointmentStartProcessor(CyodaProcessor):
    """Processor to mark appointment as in progress."""

    def __init__(self, name: str = "AppointmentStartProcessor", description: str = ""):
        super().__init__(
            name=name, description=description or "Mark appointment as in progress"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process appointment start."""
        try:
            if not isinstance(entity, Appointment):
                raise ProcessorError(
                    self.name, f"Expected Appointment entity, got {type(entity)}"
                )

            appointment = entity

            # Verify current time is appointment time
            await self._verify_current_time_is_appointment_time(
                appointment.appointment_date
            )

            # Check pet and owner presence
            await self._check_pet_and_owner_presence(
                appointment.pet_id, appointment.owner_id
            )

            # Notify vet of start
            await self._notify_vet_of_start(appointment.vet_id, appointment)

            # Start appointment timer
            await self._start_appointment_timer(appointment)

            # Log start event
            appointment.add_metadata("start_processor", self.name)
            appointment.add_metadata(
                "start_timestamp", datetime.now(timezone.utc).isoformat()
            )

            logger.info(
                f"Successfully started appointment {appointment.appointment_id}"
            )

            return appointment

        except Exception as e:
            logger.exception(f"Failed to start appointment {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to start appointment: {str(e)}", e)

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Appointment)

    async def _verify_current_time_is_appointment_time(
        self, appointment_date: str
    ) -> None:
        """Verify current time is appointment time."""
        logger.info(f"Verifying appointment time: {appointment_date}")
        # TODO: Implement actual time verification

    async def _check_pet_and_owner_presence(self, pet_id: str, owner_id: str) -> None:
        """Check pet and owner presence."""
        logger.info(f"Checking presence of pet {pet_id} and owner {owner_id}")
        # TODO: Implement actual presence check

    async def _notify_vet_of_start(self, vet_id: str, appointment: Appointment) -> None:
        """Notify vet of start."""
        logger.info(f"Notifying vet {vet_id} of appointment start")
        # TODO: Implement actual notification

    async def _start_appointment_timer(self, appointment: Appointment) -> None:
        """Start appointment timer."""
        logger.info(f"Starting timer for appointment {appointment.appointment_id}")
        # TODO: Implement actual timer
