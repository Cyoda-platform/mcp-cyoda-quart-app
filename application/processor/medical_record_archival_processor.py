"""
Medical Record Archival Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.medicalrecord.version_1.medicalrecord import MedicalRecord
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class MedicalRecordArchivalProcessor(CyodaProcessor):
    """Processor to archive a medical record."""
    
    def __init__(self, name: str = "MedicalRecordArchivalProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Archive a medical record"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process medical record archival."""
        try:
            if not isinstance(entity, MedicalRecord):
                raise ProcessorError(self.name, f"Expected MedicalRecord entity, got {type(entity)}")
            
            record = entity
            
            # Move to long-term storage
            await self._move_to_long_term_storage(record)
            
            # Update pet medical summary (no transition)
            await self._update_pet_medical_summary(record.pet_id, record)
            
            # Create archival index
            await self._create_archival_index(record)
            
            # Log archival event
            record.add_metadata("archival_processor", self.name)
            record.add_metadata("archival_timestamp", datetime.now(timezone.utc).isoformat())
            record.add_metadata("record_status", "archived")
            
            logger.info(f"Successfully archived medical record {record.record_id}")
            
            return record
            
        except Exception as e:
            logger.exception(f"Failed to archive medical record {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to archive medical record: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, MedicalRecord)
    
    async def _move_to_long_term_storage(self, record: MedicalRecord) -> None:
        """Move to long-term storage."""
        logger.info(f"Moving record {record.record_id} to long-term storage")
        # TODO: Implement actual storage move
    
    async def _update_pet_medical_summary(self, pet_id: str, record: MedicalRecord) -> None:
        """Update pet medical summary (no transition)."""
        logger.info(f"Updating medical summary for pet {pet_id}")
        # TODO: Update pet without transition
    
    async def _create_archival_index(self, record: MedicalRecord) -> None:
        """Create archival index."""
        logger.info(f"Creating archival index for record {record.record_id}")
        # TODO: Implement actual index creation
