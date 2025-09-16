"""
Appointment Scheduling Criterion for Purrfect Pets API.

Validates that an appointment can be scheduled.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.appointment.version_1.appointment import Appointment
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError

logger = logging.getLogger(__name__)


class AppointmentSchedulingCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate appointment scheduling requirements."""
    
    def __init__(self, name: str = "AppointmentSchedulingCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Validate that an appointment can be scheduled"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if the appointment meets scheduling criteria."""
        try:
            if not isinstance(entity, Appointment):
                logger.warning(f"Expected Appointment entity, got {type(entity)}")
                return False
            
            appointment = entity
            
            # Check if appointment is in the future
            if not self._is_appointment_in_future(appointment.appointment_date):
                logger.info(f"Appointment date validation failed for appointment {appointment.appointment_id}")
                return False
            
            # Check if duration is reasonable
            if not self._is_duration_reasonable(appointment.duration_minutes):
                logger.info(f"Duration validation failed for appointment {appointment.appointment_id}")
                return False
            
            # Check if appointment type is valid
            if not self._is_appointment_type_valid(appointment.appointment_type):
                logger.info(f"Appointment type validation failed for appointment {appointment.appointment_id}")
                return False
            
            logger.info(f"All scheduling validations passed for appointment {appointment.appointment_id}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check appointment scheduling criteria for entity {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check appointment scheduling criteria: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Appointment)
    
    def _is_appointment_in_future(self, appointment_date: str) -> bool:
        """Check if appointment is scheduled for the future."""
        try:
            appointment_dt = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
            current_dt = datetime.now(timezone.utc)
            return appointment_dt > current_dt
        except ValueError:
            return False
    
    def _is_duration_reasonable(self, duration_minutes: int) -> bool:
        """Check if duration is reasonable."""
        return 15 <= duration_minutes <= 480  # 15 minutes to 8 hours
    
    def _is_appointment_type_valid(self, appointment_type: str) -> bool:
        """Check if appointment type is valid."""
        if not appointment_type:
            return False
        
        valid_types = {
            'checkup', 'vaccination', 'surgery', 'dental', 'grooming',
            'emergency', 'consultation', 'follow-up', 'spay/neuter',
            'x-ray', 'blood work', 'medication check'
        }
        
        return appointment_type.lower() in valid_types
