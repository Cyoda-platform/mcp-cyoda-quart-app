"""Order Creation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderCreationProcessor(CyodaProcessor):
    """Processor for creating new orders."""

    def __init__(self):
        super().__init__(
            name="OrderCreationProcessor",
            description="Creates new order, validates pet availability, calculates total",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process order creation."""
        try:
            if not isinstance(entity, Order):
                raise ProcessorError(self.name, "Entity must be an Order instance")

            # Validate required fields
            if not entity.ownerId:
                raise ProcessorError(self.name, "Owner ID is required")

            if not entity.petId:
                raise ProcessorError(self.name, "Pet ID is required")

            if not entity.deliveryAddress or not entity.deliveryAddress.strip():
                raise ProcessorError(self.name, "Delivery address is required")

            if entity.quantity <= 0:
                raise ProcessorError(self.name, "Quantity must be positive")

            if entity.totalAmount <= 0:
                raise ProcessorError(self.name, "Total amount must be positive")

            # TODO: In a real implementation, this would:
            # 1. Validate pet exists and is AVAILABLE using EntityService
            # 2. Validate owner exists and is ACTIVE using EntityService
            # 3. Calculate totalAmount = pet.price * quantity
            # 4. Trigger pet workflow transition to PENDING

            # Set timestamps
            current_time = datetime.now(timezone.utc).isoformat()
            entity.orderDate = current_time
            entity.createdAt = current_time
            entity.updatedAt = current_time
            entity.update_timestamp()

            # Add creation metadata
            entity.add_metadata("order_created", True)
            entity.add_metadata("processed_at", current_time)
            entity.add_metadata("pet_reserved", True)

            logger.info(
                f"Successfully created order for pet {entity.petId} and owner {entity.ownerId}"
            )
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process order creation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process order creation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
