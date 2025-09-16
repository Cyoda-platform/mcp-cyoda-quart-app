"""
Appointment Confirmation Processor for Purrfect Pets API.
"""

import logging
from datetime import datetime, timezone

from application.entity.appointment.version_1.appointment import Appointment
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class AppointmentConfirmationProcessor(CyodaProcessor):
    """Processor to confirm an appointment."""

    def __init__(
        self, name: str = "AppointmentConfirmationProcessor", description: str = ""
    ):
        super().__init__(name=name, description=description or "Confirm an appointment")

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process appointment confirmation."""
        try:
            if not isinstance(entity, Appointment):
                raise ProcessorError(
                    self.name, f"Expected Appointment entity, got {type(entity)}"
                )

            appointment = entity

            # Send confirmation to owner
            await self._send_confirmation_to_owner(appointment.owner_id, appointment)

            # Send notification to vet
            await self._send_notification_to_vet(appointment.vet_id, appointment)

            # Update calendar systems
            await self._update_calendar_systems(appointment)

            # Set reminder notifications
            await self._set_reminder_notifications(appointment)

            # Log confirmation event
            appointment.add_metadata("confirmation_processor", self.name)
            appointment.add_metadata(
                "confirmation_timestamp", datetime.now(timezone.utc).isoformat()
            )

            logger.info(
                f"Successfully confirmed appointment {appointment.appointment_id}"
            )

            return appointment

        except Exception as e:
            logger.exception(f"Failed to confirm appointment {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to confirm appointment: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Appointment)

    async def _send_confirmation_to_owner(
        self, owner_id: str, appointment: Appointment
    ) -> None:
        """Send confirmation to owner."""
        logger.info(
            f"Sending confirmation to owner {owner_id} for appointment {appointment.appointment_id}"
        )
        # TODO: Implement actual confirmation sending

    async def _send_notification_to_vet(
        self, vet_id: str, appointment: Appointment
    ) -> None:
        """Send notification to vet."""
        logger.info(
            f"Sending notification to vet {vet_id} for appointment {appointment.appointment_id}"
        )
        # TODO: Implement actual notification sending

    async def _update_calendar_systems(self, appointment: Appointment) -> None:
        """Update calendar systems."""
        logger.info(
            f"Updating calendar systems for appointment {appointment.appointment_id}"
        )
        # TODO: Implement actual calendar update

    async def _set_reminder_notifications(self, appointment: Appointment) -> None:
        """Set reminder notifications."""
        logger.info(
            f"Setting reminder notifications for appointment {appointment.appointment_id}"
        )
        # TODO: Implement actual reminder setting
