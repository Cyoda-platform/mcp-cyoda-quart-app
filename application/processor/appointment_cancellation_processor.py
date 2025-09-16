"""
Appointment Cancellation Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.appointment.version_1.appointment import Appointment
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class AppointmentCancellationProcessor(CyodaProcessor):
    """Processor to cancel an appointment."""
    
    def __init__(self, name: str = "AppointmentCancellationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Cancel an appointment"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process appointment cancellation."""
        try:
            if not isinstance(entity, Appointment):
                raise ProcessorError(self.name, f"Expected Appointment entity, got {type(entity)}")
            
            appointment = entity
            
            # Free time slot
            await self._free_time_slot(appointment)
            
            # Notify all parties
            await self._notify_all_parties(appointment.owner_id, appointment.vet_id, appointment)
            
            # Apply cancellation policy
            await self._apply_cancellation_policy(appointment)
            
            # Update calendar systems
            await self._update_calendar_systems(appointment)
            
            # Log cancellation event
            appointment.add_metadata("cancellation_processor", self.name)
            appointment.add_metadata("cancellation_timestamp", datetime.now(timezone.utc).isoformat())
            appointment.add_metadata("cancellation_reason", kwargs.get("reason", "Manual cancellation"))
            
            logger.info(f"Successfully cancelled appointment {appointment.appointment_id}")
            
            return appointment
            
        except Exception as e:
            logger.exception(f"Failed to cancel appointment {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to cancel appointment: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Appointment)
    
    async def _free_time_slot(self, appointment: Appointment) -> None:
        """Free time slot."""
        logger.info(f"Freeing time slot for appointment {appointment.appointment_id}")
        # TODO: Implement actual time slot freeing
    
    async def _notify_all_parties(self, owner_id: str, vet_id: str, appointment: Appointment) -> None:
        """Notify all parties."""
        logger.info(f"Notifying all parties for appointment {appointment.appointment_id}")
        # TODO: Implement actual notifications
    
    async def _apply_cancellation_policy(self, appointment: Appointment) -> None:
        """Apply cancellation policy."""
        logger.info(f"Applying cancellation policy for appointment {appointment.appointment_id}")
        # TODO: Implement actual policy application
    
    async def _update_calendar_systems(self, appointment: Appointment) -> None:
        """Update calendar systems."""
        logger.info(f"Updating calendar systems for appointment {appointment.appointment_id}")
        # TODO: Implement actual calendar update
