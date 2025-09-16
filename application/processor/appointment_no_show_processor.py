"""
Appointment No Show Processor for Purrfect Pets API.
"""

import logging
from datetime import datetime, timezone

from application.entity.appointment.version_1.appointment import Appointment
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class AppointmentNoShowProcessor(CyodaProcessor):
    """Processor to mark appointment as no-show."""

    def __init__(self, name: str = "AppointmentNoShowProcessor", description: str = ""):
        super().__init__(
            name=name, description=description or "Mark appointment as no-show"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process appointment no-show."""
        try:
            if not isinstance(entity, Appointment):
                raise ProcessorError(
                    self.name, f"Expected Appointment entity, got {type(entity)}"
                )

            appointment = entity

            # Verify appointment time passed
            await self._verify_appointment_time_passed(appointment.appointment_date)

            # Apply no show policy
            await self._apply_no_show_policy(appointment)

            # Notify vet of no show
            await self._notify_vet_of_no_show(appointment.vet_id, appointment)

            # Free time slot
            await self._free_time_slot(appointment)

            # Update owner no show count (no transition)
            await self._update_owner_no_show_count(appointment.owner_id)

            # Log no show event
            appointment.add_metadata("no_show_processor", self.name)
            appointment.add_metadata(
                "no_show_timestamp", datetime.now(timezone.utc).isoformat()
            )

            logger.info(f"Marked appointment {appointment.appointment_id} as no-show")

            return appointment

        except Exception as e:
            logger.exception(
                f"Failed to mark appointment as no-show {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to mark appointment as no-show: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Appointment)

    async def _verify_appointment_time_passed(self, appointment_date: str) -> None:
        """Verify appointment time passed."""
        logger.info(f"Verifying appointment time passed: {appointment_date}")
        # TODO: Implement actual time verification

    async def _apply_no_show_policy(self, appointment: Appointment) -> None:
        """Apply no show policy."""
        logger.info(
            f"Applying no show policy for appointment {appointment.appointment_id}"
        )
        # TODO: Implement actual policy application

    async def _notify_vet_of_no_show(
        self, vet_id: str, appointment: Appointment
    ) -> None:
        """Notify vet of no show."""
        logger.info(f"Notifying vet {vet_id} of no show")
        # TODO: Implement actual notification

    async def _free_time_slot(self, appointment: Appointment) -> None:
        """Free time slot."""
        logger.info(f"Freeing time slot for appointment {appointment.appointment_id}")
        # TODO: Implement actual time slot freeing

    async def _update_owner_no_show_count(self, owner_id: str) -> None:
        """Update owner no show count (no transition)."""
        logger.info(f"Updating no show count for owner {owner_id}")
        # TODO: Update owner without transition
