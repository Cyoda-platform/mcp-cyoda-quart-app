"""
Medical Record Creation Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.medicalrecord.version_1.medicalrecord import MedicalRecord
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class MedicalRecordCreationProcessor(CyodaProcessor):
    """Processor to create a new medical record."""
    
    def __init__(self, name: str = "MedicalRecordCreationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Create a new medical record"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process medical record creation."""
        try:
            if not isinstance(entity, MedicalRecord):
                raise ProcessorError(self.name, f"Expected MedicalRecord entity, got {type(entity)}")
            
            record = entity
            
            # Validate required fields
            self._validate_required_fields(record)
            
            # Verify pet exists
            await self._verify_pet_exists(record.pet_id)
            
            # Verify vet exists
            await self._verify_vet_exists(record.vet_id)
            
            # Set created date if not already set
            if not record.created_date:
                record.created_date = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            # Generate unique record_id if not provided
            if not record.record_id:
                record.record_id = f"MED-{record.entity_id[:8].upper()}"
            
            # Initialize draft record
            await self._initialize_draft_record(record)
            
            # Log creation event
            record.add_metadata("creation_processor", self.name)
            record.add_metadata("creation_timestamp", datetime.now(timezone.utc).isoformat())
            
            logger.info(f"Successfully created medical record {record.record_id}")
            
            return record
            
        except Exception as e:
            logger.exception(f"Failed to create medical record {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to create medical record: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, MedicalRecord)
    
    def _validate_required_fields(self, record: MedicalRecord) -> None:
        """Validate required fields."""
        required_fields = ['pet_id', 'vet_id', 'visit_date']
        for field in required_fields:
            if not getattr(record, field):
                raise ValueError(f"{field} is required")
    
    async def _verify_pet_exists(self, pet_id: str) -> None:
        """Verify pet exists."""
        logger.debug(f"Verifying pet {pet_id} exists")
        # TODO: Implement actual pet verification
    
    async def _verify_vet_exists(self, vet_id: str) -> None:
        """Verify vet exists."""
        logger.debug(f"Verifying vet {vet_id} exists")
        # TODO: Implement actual vet verification
    
    async def _initialize_draft_record(self, record: MedicalRecord) -> None:
        """Initialize draft record."""
        logger.info(f"Initializing draft record {record.record_id}")
        record.add_metadata("record_status", "draft")
        # TODO: Implement actual draft initialization
