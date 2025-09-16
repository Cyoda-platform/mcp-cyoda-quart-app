"""Pet Sale Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class PetSaleProcessor(CyodaProcessor):
    """Processor for completing pet sales."""

    def __init__(self):
        super().__init__(
            name="PetSaleProcessor",
            description="Completes pet sale, creates order record, updates pet status",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet sale."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(self.name, "Entity must be a Pet instance")

            # Validate pet is pending
            if entity.state not in ["pending"]:
                raise ProcessorError(
                    self.name,
                    f"Pet must be pending for sale, current state: {entity.state}",
                )

            # Validate owner is set
            if not entity.ownerId:
                raise ProcessorError(self.name, "Pet must have an owner for sale")

            # Get order details from kwargs
            order_details = kwargs.get("orderDetails", {})

            # TODO: In a real implementation, this would:
            # 1. Validate owner is ACTIVE using EntityService
            # 2. Create new order entity using EntityService
            # 3. Set order.totalAmount = pet.price
            # 4. Save order to database
            # 5. Trigger order workflow transition to PLACED

            # Update pet timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add sale metadata
            entity.add_metadata("sold_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("sold_to", entity.ownerId)
            entity.add_metadata("sale_processed", True)
            entity.add_metadata("order_details", order_details)

            logger.info(
                f"Successfully processed sale for pet {entity.name} to owner {entity.ownerId}"
            )
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process pet sale for entity {entity.entity_id}"
            )
            raise ProcessorError(self.name, f"Failed to process pet sale: {str(e)}", e)

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Pet"
        )
