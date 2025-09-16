"""
Medical Record Completion Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.medicalrecord.version_1.medicalrecord import MedicalRecord
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class MedicalRecordCompletionProcessor(CyodaProcessor):
    """Processor to complete a medical record."""
    
    def __init__(self, name: str = "MedicalRecordCompletionProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Complete a medical record"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process medical record completion."""
        try:
            if not isinstance(entity, MedicalRecord):
                raise ProcessorError(self.name, f"Expected MedicalRecord entity, got {type(entity)}")
            
            record = entity
            
            # Validate medical content
            await self._validate_medical_content(record)
            
            # Calculate total cost
            total_cost = await self._calculate_total_cost(record)
            if total_cost is not None:
                record.cost = total_cost
            
            # Set follow-up requirements
            await self._set_follow_up_requirements(record)
            
            # Notify owner of record
            await self._notify_owner_of_record(record.pet_id, record)
            
            # Update pet medical history (no transition)
            await self._update_pet_medical_history(record.pet_id, record)
            
            # Log completion event
            record.add_metadata("completion_processor", self.name)
            record.add_metadata("completion_timestamp", datetime.now(timezone.utc).isoformat())
            record.add_metadata("record_status", "completed")
            
            logger.info(f"Successfully completed medical record {record.record_id}")
            
            return record
            
        except Exception as e:
            logger.exception(f"Failed to complete medical record {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to complete medical record: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, MedicalRecord)
    
    async def _validate_medical_content(self, record: MedicalRecord) -> None:
        """Validate medical content."""
        logger.info(f"Validating medical content for record {record.record_id}")
        # TODO: Implement actual medical content validation
    
    async def _calculate_total_cost(self, record: MedicalRecord) -> float:
        """Calculate total cost."""
        logger.info(f"Calculating total cost for record {record.record_id}")
        # TODO: Implement actual cost calculation
        return record.cost  # Return existing cost if any
    
    async def _set_follow_up_requirements(self, record: MedicalRecord) -> None:
        """Set follow-up requirements."""
        logger.info(f"Setting follow-up requirements for record {record.record_id}")
        # TODO: Implement actual follow-up requirement setting
    
    async def _notify_owner_of_record(self, pet_id: str, record: MedicalRecord) -> None:
        """Notify owner of record."""
        logger.info(f"Notifying owner of medical record {record.record_id} for pet {pet_id}")
        # TODO: Get owner through pet and send notification
    
    async def _update_pet_medical_history(self, pet_id: str, record: MedicalRecord) -> None:
        """Update pet medical history (no transition)."""
        logger.info(f"Updating medical history for pet {pet_id}")
        # TODO: Update pet without transition
