"""
Owner Archival Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class OwnerArchivalProcessor(CyodaProcessor):
    """Processor to permanently archive an owner record."""
    
    def __init__(self, name: str = "OwnerArchivalProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Permanently archive an owner record"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner archival."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, f"Expected Owner entity, got {type(entity)}")
            
            owner = entity
            
            # Archive all pets with transition "archive"
            await self._archive_all_pets(owner.owner_id)
            
            # Cancel all appointments
            await self._cancel_all_appointments(owner.owner_id)
            
            # Archive medical records (no transition)
            await self._archive_medical_records(owner.owner_id)
            
            # Revoke all access
            await self._revoke_all_access(owner.owner_id)
            
            # Create archival record
            await self._create_archival_record(owner)
            
            # Log archival event
            owner.add_metadata("archival_processor", self.name)
            owner.add_metadata("archival_timestamp", datetime.now(timezone.utc).isoformat())
            
            logger.info(f"Successfully archived owner {owner.owner_id}")
            
            return owner
            
        except Exception as e:
            logger.exception(f"Failed to archive owner {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to archive owner: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner)
    
    async def _archive_all_pets(self, owner_id: str) -> None:
        """Archive all pets with transition."""
        logger.info(f"Archiving all pets for owner {owner_id}")
        # TODO: Update pets with transition "archive"
    
    async def _cancel_all_appointments(self, owner_id: str) -> None:
        """Cancel all appointments."""
        logger.info(f"Cancelling all appointments for owner {owner_id}")
        # TODO: Implement actual appointment cancellation
    
    async def _archive_medical_records(self, owner_id: str) -> None:
        """Archive medical records (no transition)."""
        logger.info(f"Archiving medical records for owner {owner_id}")
        # TODO: Update medical records without transition
    
    async def _revoke_all_access(self, owner_id: str) -> None:
        """Revoke all access."""
        logger.info(f"Revoking all access for owner {owner_id}")
        # TODO: Implement actual access revocation
    
    async def _create_archival_record(self, owner: Owner) -> None:
        """Create archival record."""
        archival_record = {
            "owner_id": owner.owner_id,
            "owner_name": owner.get_full_name(),
            "email": owner.email,
            "archival_date": datetime.now(timezone.utc).isoformat()
        }
        logger.info(f"Archival record created: {archival_record}")
        # TODO: Store archival record
