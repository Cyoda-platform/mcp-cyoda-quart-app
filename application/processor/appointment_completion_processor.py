"""
Appointment Completion Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.appointment.version_1.appointment import Appointment
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class AppointmentCompletionProcessor(CyodaProcessor):
    """Processor to complete an appointment."""
    
    def __init__(self, name: str = "AppointmentCompletionProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Complete an appointment"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process appointment completion."""
        try:
            if not isinstance(entity, Appointment):
                raise ProcessorError(self.name, f"Expected Appointment entity, got {type(entity)}")
            
            appointment = entity
            
            # Calculate actual duration
            actual_duration = await self._calculate_actual_duration(appointment)
            
            # Create medical record with transition "create"
            await self._create_medical_record(appointment)
            
            # Update pet last visit date (no transition)
            await self._update_pet_last_visit_date(appointment.pet_id)
            
            # Send completion notification
            await self._send_completion_notification(appointment.owner_id, appointment)
            
            # Free time slot
            await self._free_time_slot(appointment)
            
            # Log completion event
            appointment.add_metadata("completion_processor", self.name)
            appointment.add_metadata("completion_timestamp", datetime.now(timezone.utc).isoformat())
            appointment.add_metadata("actual_duration_minutes", actual_duration)
            
            logger.info(f"Successfully completed appointment {appointment.appointment_id}")
            
            return appointment
            
        except Exception as e:
            logger.exception(f"Failed to complete appointment {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to complete appointment: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Appointment)
    
    async def _calculate_actual_duration(self, appointment: Appointment) -> int:
        """Calculate actual duration."""
        logger.info(f"Calculating actual duration for appointment {appointment.appointment_id}")
        # TODO: Implement actual duration calculation
        return appointment.duration_minutes  # Default to scheduled duration
    
    async def _create_medical_record(self, appointment: Appointment) -> None:
        """Create medical record with transition."""
        logger.info(f"Creating medical record for appointment {appointment.appointment_id}")
        # TODO: Create medical record with transition "create"
    
    async def _update_pet_last_visit_date(self, pet_id: str) -> None:
        """Update pet last visit date (no transition)."""
        logger.info(f"Updating last visit date for pet {pet_id}")
        # TODO: Update pet without transition
    
    async def _send_completion_notification(self, owner_id: str, appointment: Appointment) -> None:
        """Send completion notification."""
        logger.info(f"Sending completion notification to owner {owner_id}")
        # TODO: Implement actual notification
    
    async def _free_time_slot(self, appointment: Appointment) -> None:
        """Free time slot."""
        logger.info(f"Freeing time slot for appointment {appointment.appointment_id}")
        # TODO: Implement actual time slot freeing
