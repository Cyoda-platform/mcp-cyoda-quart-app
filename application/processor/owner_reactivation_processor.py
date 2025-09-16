"""
Owner Reactivation Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class OwnerReactivationProcessor(CyodaProcessor):
    """Processor to reactivate a suspended owner."""
    
    def __init__(self, name: str = "OwnerReactivationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Reactivate a suspended owner"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner reactivation."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, f"Expected Owner entity, got {type(entity)}")
            
            owner = entity
            
            # Restore system access
            await self._restore_system_access(owner.owner_id)
            
            # Reactivate pets with transition "reactivate"
            await self._reactivate_pets(owner.owner_id)
            
            # Send reactivation notification
            await self._send_reactivation_notification(owner.email)
            
            # Log reactivation event
            owner.add_metadata("reactivation_processor", self.name)
            owner.add_metadata("reactivation_timestamp", datetime.now(timezone.utc).isoformat())
            
            logger.info(f"Successfully reactivated owner {owner.owner_id}")
            
            return owner
            
        except Exception as e:
            logger.exception(f"Failed to reactivate owner {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to reactivate owner: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner)
    
    async def _restore_system_access(self, owner_id: str) -> None:
        """Restore system access."""
        logger.info(f"Restoring system access for owner {owner_id}")
        # TODO: Implement actual access restoration
    
    async def _reactivate_pets(self, owner_id: str) -> None:
        """Reactivate pets with transition."""
        logger.info(f"Reactivating pets for owner {owner_id}")
        # TODO: Update pets with transition "reactivate"
    
    async def _send_reactivation_notification(self, email: str) -> None:
        """Send reactivation notification."""
        logger.info(f"Sending reactivation notification to {email}")
        # TODO: Implement actual notification
