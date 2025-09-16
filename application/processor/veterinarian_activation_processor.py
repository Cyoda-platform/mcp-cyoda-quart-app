"""
Veterinarian Activation Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.veterinarian.version_1.veterinarian import Veterinarian
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class VeterinarianActivationProcessor(CyodaProcessor):
    """Processor to activate veterinarian for appointments."""
    
    def __init__(self, name: str = "VeterinarianActivationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Activate veterinarian for appointments"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process veterinarian activation."""
        try:
            if not isinstance(entity, Veterinarian):
                raise ProcessorError(self.name, f"Expected Veterinarian entity, got {type(entity)}")
            
            vet = entity
            
            # Set veterinarian as available
            vet.is_available = True
            
            # Create appointment schedule
            await self._create_appointment_schedule(vet.vet_id)
            
            # Grant system access
            await self._grant_system_access(vet.vet_id)
            
            # Send welcome email
            await self._send_welcome_email(vet.email, vet.get_full_name())
            
            # Log activation event
            vet.add_metadata("activation_processor", self.name)
            vet.add_metadata("activation_timestamp", datetime.now(timezone.utc).isoformat())
            
            logger.info(f"Successfully activated veterinarian {vet.vet_id}")
            
            return vet
            
        except Exception as e:
            logger.exception(f"Failed to activate veterinarian {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to activate veterinarian: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Veterinarian)
    
    async def _create_appointment_schedule(self, vet_id: str) -> None:
        """Create appointment schedule."""
        logger.info(f"Creating appointment schedule for veterinarian {vet_id}")
        # TODO: Implement actual schedule creation
    
    async def _grant_system_access(self, vet_id: str) -> None:
        """Grant system access."""
        logger.info(f"Granting system access to veterinarian {vet_id}")
        # TODO: Implement actual access granting
    
    async def _send_welcome_email(self, email: str, full_name: str) -> None:
        """Send welcome email."""
        logger.info(f"Sending welcome email to {email} for {full_name}")
        # TODO: Implement actual email sending
