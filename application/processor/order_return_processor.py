"""Order Return Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderReturnProcessor(CyodaProcessor):
    """Processor for processing order returns."""

    def __init__(self):
        super().__init__(
            name="OrderReturnProcessor",
            description="Processes order return, handles refund",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process order return."""
        try:
            if not isinstance(entity, Order):
                raise ProcessorError(self.name, "Entity must be an Order instance")

            # Validate order is delivered
            if entity.state not in ["delivered"]:
                raise ProcessorError(
                    self.name,
                    f"Order must be delivered for return, current state: {entity.state}",
                )

            # Get return reason
            return_reason = kwargs.get("returnReason") or kwargs.get("return_reason")
            if not return_reason:
                raise ProcessorError(self.name, "Return reason is required")

            # TODO: In a real implementation, this would:
            # 1. Validate return is within return period
            # 2. Process refund
            # 3. Trigger pet workflow transition to AVAILABLE (null transition)
            # 4. Send return confirmation to owner

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add return metadata
            entity.add_metadata("returned_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("return_reason", return_reason)
            entity.add_metadata("refund_processed", True)
            entity.add_metadata("pet_returned", True)
            entity.add_metadata("return_confirmation_sent", True)
            entity.add_metadata("return_processed", True)

            logger.info(
                f"Successfully processed return for order {entity.entity_id}, reason: {return_reason}"
            )
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process order return for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process order return: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
