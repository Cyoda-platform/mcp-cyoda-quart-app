"""Order Preparation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderPreparationProcessor(CyodaProcessor):
    """Processor for preparing orders for delivery."""

    def __init__(self):
        super().__init__(
            name="OrderPreparationProcessor",
            description="Begins order preparation, schedules delivery",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process order preparation."""
        try:
            if not isinstance(entity, Order):
                raise ProcessorError(self.name, "Entity must be an Order instance")

            # Validate order is confirmed
            if entity.state not in ["confirmed"]:
                raise ProcessorError(
                    self.name,
                    f"Order must be confirmed for preparation, current state: {entity.state}",
                )

            # Schedule delivery date (3-5 days from now)
            delivery_date = (
                (datetime.now(timezone.utc) + timedelta(days=4)).date().isoformat()
            )
            entity.deliveryDate = delivery_date

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add preparation metadata
            entity.add_metadata(
                "preparation_started", datetime.now(timezone.utc).isoformat()
            )
            entity.add_metadata("delivery_scheduled", delivery_date)
            entity.add_metadata("documentation_prepared", True)
            entity.add_metadata("preparation_notification_sent", True)
            entity.add_metadata("preparation_processed", True)

            logger.info(
                f"Successfully started preparation for order {entity.entity_id}, delivery scheduled for {delivery_date}"
            )
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process order preparation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process order preparation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
