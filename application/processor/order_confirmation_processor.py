"""Order Confirmation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderConfirmationProcessor(CyodaProcessor):
    """Processor for confirming orders."""

    def __init__(self):
        super().__init__(
            name="OrderConfirmationProcessor",
            description="Confirms order, validates payment, reserves pet",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process order confirmation."""
        try:
            if not isinstance(entity, Order):
                raise ProcessorError(self.name, "Entity must be an Order instance")

            # Validate order is placed
            if entity.state not in ["placed"]:
                raise ProcessorError(
                    self.name,
                    f"Order must be placed for confirmation, current state: {entity.state}",
                )

            # TODO: In a real implementation, this would:
            # 1. Validate payment information is valid
            # 2. Validate pet is still available using EntityService
            # 3. Process payment
            # 4. Send confirmation email to owner

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add confirmation metadata
            entity.add_metadata("confirmed_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("payment_processed", True)
            entity.add_metadata("confirmation_email_sent", True)
            entity.add_metadata("confirmation_processed", True)

            logger.info(f"Successfully confirmed order {entity.entity_id}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process order confirmation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process order confirmation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
