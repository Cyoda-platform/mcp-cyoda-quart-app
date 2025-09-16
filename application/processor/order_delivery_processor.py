"""Order Delivery Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderDeliveryProcessor(CyodaProcessor):
    """Processor for confirming order delivery."""

    def __init__(self):
        super().__init__(
            name="OrderDeliveryProcessor",
            description="Confirms delivery, completes order",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process order delivery."""
        try:
            if not isinstance(entity, Order):
                raise ProcessorError(self.name, "Entity must be an Order instance")

            # Validate order is shipped
            if entity.state not in ["shipped"]:
                raise ProcessorError(
                    self.name,
                    f"Order must be shipped for delivery, current state: {entity.state}",
                )

            # Get delivery confirmation
            delivery_confirmation = kwargs.get("deliveryConfirmation") or kwargs.get(
                "delivery_confirmation", {}
            )

            # TODO: In a real implementation, this would:
            # 1. Validate delivery confirmation
            # 2. Trigger pet workflow transition to SOLD
            # 3. Send delivery confirmation to owner

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add delivery metadata
            entity.add_metadata("delivered_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("delivery_confirmed", True)
            entity.add_metadata("pet_transferred", True)
            entity.add_metadata("delivery_confirmation_sent", True)
            entity.add_metadata("delivery_processed", True)

            if delivery_confirmation:
                entity.add_metadata("delivery_confirmation", delivery_confirmation)

            logger.info(f"Successfully delivered order {entity.entity_id}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process order delivery for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process order delivery: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
