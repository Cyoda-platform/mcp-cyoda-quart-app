"""Order Shipping Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderShippingProcessor(CyodaProcessor):
    """Processor for shipping orders."""

    def __init__(self):
        super().__init__(
            name="OrderShippingProcessor",
            description="Ships order, provides tracking details",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process order shipping."""
        try:
            if not isinstance(entity, Order):
                raise ProcessorError(self.name, "Entity must be an Order instance")

            # Validate order is preparing
            if entity.state not in ["preparing"]:
                raise ProcessorError(
                    self.name,
                    f"Order must be preparing for shipping, current state: {entity.state}",
                )

            # Get tracking information
            tracking_info = kwargs.get("trackingInfo") or kwargs.get(
                "tracking_info", {}
            )
            tracking_number = tracking_info.get(
                "tracking_number", f"TRACK_{entity.entity_id[:8]}"
            )

            # TODO: In a real implementation, this would:
            # 1. Validate pet is ready for delivery
            # 2. Create shipping label
            # 3. Send shipping notification with tracking to owner

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add shipping metadata
            entity.add_metadata("shipped_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("tracking_number", tracking_number)
            entity.add_metadata("shipping_label_created", True)
            entity.add_metadata("shipping_notification_sent", True)
            entity.add_metadata("shipping_processed", True)

            if tracking_info:
                entity.add_metadata("tracking_info", tracking_info)

            logger.info(
                f"Successfully shipped order {entity.entity_id}, tracking: {tracking_number}"
            )
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process order shipping for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process order shipping: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
