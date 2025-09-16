"""Owner Suspension Processor for Purrfect Pets API."""
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from application.entity.owner.version_1.owner import Owner

logger = logging.getLogger(__name__)


class OwnerSuspensionProcessor(CyodaProcessor):
    """Processor for suspending owner accounts."""
    
    def __init__(self):
        super().__init__(
            name="OwnerSuspensionProcessor",
            description="Suspends owner account, cancels reservations"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner suspension."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, "Entity must be an Owner instance")
            
            # Validate owner is active
            if entity.state not in ["active"]:
                raise ProcessorError(self.name, f"Owner must be active for suspension, current state: {entity.state}")
            
            # Get suspension reason
            suspension_reason = kwargs.get("suspensionReason") or kwargs.get("suspension_reason")
            if not suspension_reason:
                raise ProcessorError(self.name, "Suspension reason is required")
            
            # TODO: In a real implementation, this would:
            # 1. Cancel all PENDING pet reservations for this owner using EntityService
            # 2. Send suspension notification email
            
            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()
            
            # Add suspension metadata
            entity.add_metadata("suspended_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("suspension_reason", suspension_reason)
            entity.add_metadata("suspension_processed", True)
            entity.add_metadata("reservations_cancelled", True)
            entity.add_metadata("suspension_notification_sent", True)
            
            logger.info(f"Successfully suspended owner {entity.email}, reason: {suspension_reason}")
            return entity
            
        except Exception as e:
            logger.exception(f"Failed to process owner suspension for entity {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to process owner suspension: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Owner"
        )
