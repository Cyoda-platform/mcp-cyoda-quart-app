"""
Veterinarian Availability Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.veterinarian.version_1.veterinarian import Veterinarian
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class VeterinarianAvailabilityProcessor(CyodaProcessor):
    """Processor to mark veterinarian as available again."""
    
    def __init__(self, name: str = "VeterinarianAvailabilityProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Mark veterinarian as available again"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process veterinarian availability."""
        try:
            if not isinstance(entity, Veterinarian):
                raise ProcessorError(self.name, f"Expected Veterinarian entity, got {type(entity)}")
            
            vet = entity
            
            # Set veterinarian as available
            vet.is_available = True
            
            # Restore appointment schedule
            await self._restore_appointment_schedule(vet.vet_id)
            
            # Notify scheduling system
            await self._notify_scheduling_system(vet.vet_id)
            
            # Log availability event
            vet.add_metadata("availability_processor", self.name)
            vet.add_metadata("availability_timestamp", datetime.now(timezone.utc).isoformat())
            
            logger.info(f"Marked veterinarian {vet.vet_id} as available")
            
            return vet
            
        except Exception as e:
            logger.exception(f"Failed to mark veterinarian available {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to mark veterinarian available: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Veterinarian)
    
    async def _restore_appointment_schedule(self, vet_id: str) -> None:
        """Restore appointment schedule."""
        logger.info(f"Restoring appointment schedule for veterinarian {vet_id}")
        # TODO: Implement actual schedule restoration
    
    async def _notify_scheduling_system(self, vet_id: str) -> None:
        """Notify scheduling system."""
        logger.info(f"Notifying scheduling system for veterinarian {vet_id}")
        # TODO: Implement actual scheduling system notification
