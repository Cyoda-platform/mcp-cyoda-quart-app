"""
Owner Activation Processor for Purrfect Pets API.
"""
import logging
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity
from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError

logger = logging.getLogger(__name__)


class OwnerActivationProcessor(CyodaProcessor):
    """Processor to activate owner for full system access."""
    
    def __init__(self, name: str = "OwnerActivationProcessor", description: str = ""):
        super().__init__(
            name=name,
            description=description or "Activate owner for full system access"
        )
    
    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner activation."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, f"Expected Owner entity, got {type(entity)}")
            
            owner = entity
            
            # Grant appointment permissions
            await self._grant_appointment_permissions(owner.owner_id)
            
            # Send welcome email
            await self._send_welcome_email(owner.email, owner.get_full_name())
            
            # Create owner dashboard access
            await self._create_owner_dashboard_access(owner.owner_id)
            
            # Log activation event
            owner.add_metadata("activation_processor", self.name)
            owner.add_metadata("activation_timestamp", datetime.now(timezone.utc).isoformat())
            
            logger.info(f"Successfully activated owner {owner.owner_id}")
            
            return owner
            
        except Exception as e:
            logger.exception(f"Failed to activate owner {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to activate owner: {str(e)}", e)
    
    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner)
    
    async def _grant_appointment_permissions(self, owner_id: str) -> None:
        """Grant appointment scheduling permissions."""
        logger.info(f"Granting appointment permissions to owner {owner_id}")
        # TODO: Implement actual permission granting
    
    async def _send_welcome_email(self, email: str, full_name: str) -> None:
        """Send welcome email."""
        logger.info(f"Sending welcome email to {email} for {full_name}")
        # TODO: Implement actual email sending
    
    async def _create_owner_dashboard_access(self, owner_id: str) -> None:
        """Create owner dashboard access."""
        logger.info(f"Creating dashboard access for owner {owner_id}")
        # TODO: Implement actual dashboard access creation
