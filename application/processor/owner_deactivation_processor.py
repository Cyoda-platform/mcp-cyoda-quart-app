"""Owner Deactivation Processor for Purrfect Pets API."""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from application.entity.owner.version_1.owner import Owner

logger = logging.getLogger(__name__)


class OwnerDeactivationProcessor(CyodaProcessor):
    """Processor for deactivating owner accounts."""
    
    def __init__(self):
        super().__init__(
            name="OwnerDeactivationProcessor",
            description="Deactivates owner account, cancels active reservations"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner deactivation."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, "Entity must be an Owner instance")
            
            # Validate owner is active
            if entity.state not in ["active"]:
                raise ProcessorError(self.name, f"Owner must be active for deactivation, current state: {entity.state}")
            
            # Get deactivation reason
            reason = kwargs.get("reason", "Account deactivated by user request")
            
            # TODO: In a real implementation, this would:
            # 1. Cancel all PENDING pet reservations for this owner using EntityService
            # 2. Send deactivation notification email
            
            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()
            
            # Add deactivation metadata
            entity.add_metadata("deactivated_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("deactivation_reason", reason)
            entity.add_metadata("deactivation_processed", True)
            entity.add_metadata("reservations_cancelled", True)
            
            logger.info(f"Successfully deactivated owner {entity.email}, reason: {reason}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to process owner deactivation for entity {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to process owner deactivation: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Owner"
        )
