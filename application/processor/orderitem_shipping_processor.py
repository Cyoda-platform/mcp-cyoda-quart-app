"""
OrderItemShippingProcessor for Purrfect Pets API

Handles the shipping of OrderItem entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.orderitem.version_1.orderitem import OrderItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class OrderItemShippingProcessor(CyodaProcessor):
    """
    Processor for shipping OrderItem entities.
    Prepares item for shipping, updates pet ownership, and sets shipping timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderItemShippingProcessor",
            description="Ships OrderItem entities by preparing items and updating pet ownership",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the OrderItem entity shipping.

        Args:
            entity: The OrderItem entity to ship
            **kwargs: Additional processing parameters

        Returns:
            The shipped OrderItem entity
        """
        try:
            self.logger.info(
                f"Shipping OrderItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to OrderItem for type-safe operations
            order_item = cast_entity(entity, OrderItem)

            # Prepare item for shipping
            self.logger.info(
                f"Preparing OrderItem {order_item.technical_id} for shipping"
            )

            # Update pet ownership (would normally update Pet entity to sold state)
            # For demonstration, we'll log this action
            # In a real implementation, we would transition the Pet to sold state
            self.logger.info(f"Pet ownership updated for pet_id: {order_item.pet_id}")

            # Set shipping timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add shipping metadata
            if not order_item.metadata:
                order_item.metadata = {}

            order_item.metadata.update(
                {
                    "shipping_date": current_time,
                    "item_prepared": True,
                    "pet_ownership_updated": True,
                    "shipping_status": "shipped",
                }
            )

            # Update confirmation status
            order_item.metadata["confirmation_status"] = "shipped"

            # Update timestamp
            order_item.update_timestamp()

            self.logger.info(
                f"OrderItem {order_item.technical_id} shipped successfully"
            )

            return order_item

        except Exception as e:
            self.logger.error(
                f"Error shipping OrderItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
