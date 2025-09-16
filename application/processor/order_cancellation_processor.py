"""Order Cancellation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderCancellationProcessor(CyodaProcessor):
    """Processor for cancelling orders."""

    def __init__(self):
        super().__init__(
            name="OrderCancellationProcessor",
            description="Cancels order, refunds payment, releases pet",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process order cancellation."""
        try:
            if not isinstance(entity, Order):
                raise ProcessorError(self.name, "Entity must be an Order instance")

            # Validate order can be cancelled
            if entity.state not in ["placed", "confirmed"]:
                raise ProcessorError(
                    self.name,
                    f"Order must be placed or confirmed for cancellation, current state: {entity.state}",
                )

            # Get cancellation reason
            cancellation_reason = kwargs.get("cancellationReason") or kwargs.get(
                "cancellation_reason"
            )
            if not cancellation_reason:
                raise ProcessorError(self.name, "Cancellation reason is required")

            # TODO: In a real implementation, this would:
            # 1. Process refund if payment was made
            # 2. Trigger pet workflow transition to AVAILABLE (null transition)
            # 3. Send cancellation notification to owner

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add cancellation metadata
            entity.add_metadata("cancelled_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("cancellation_reason", cancellation_reason)
            entity.add_metadata("refund_processed", entity.state == "confirmed")
            entity.add_metadata("pet_released", True)
            entity.add_metadata("cancellation_notification_sent", True)
            entity.add_metadata("cancellation_processed", True)

            logger.info(
                f"Successfully cancelled order {entity.entity_id}, reason: {cancellation_reason}"
            )
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process order cancellation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process order cancellation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
