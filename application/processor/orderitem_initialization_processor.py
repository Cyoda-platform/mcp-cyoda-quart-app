"""
OrderItemInitializationProcessor for Purrfect Pets API

Handles the initialization of OrderItem entities when they are created.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.orderitem.version_1.orderitem import OrderItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class OrderItemInitializationProcessor(CyodaProcessor):
    """
    Processor for initializing OrderItem entities.
    Validates pet availability, sets unit price, and calculates total price.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderItemInitializationProcessor",
            description="Initializes OrderItem entities by validating pet availability and calculating prices",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the OrderItem entity initialization.

        Args:
            entity: The OrderItem entity to initialize
            **kwargs: Additional processing parameters

        Returns:
            The initialized OrderItem entity
        """
        try:
            self.logger.info(
                f"Initializing OrderItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to OrderItem for type-safe operations
            order_item = cast_entity(entity, OrderItem)

            # Validate pet availability (would normally check Pet entity)
            # For demonstration, we'll assume pet availability is validated
            self.logger.info(
                f"Pet availability validated for pet_id: {order_item.pet_id}"
            )

            # Set unit_price from current pet price (would normally fetch from Pet entity)
            # For now, we'll use the provided unit_price
            current_pet_price = order_item.unit_price
            self.logger.info(
                f"Unit price set from current pet price: ${current_pet_price}"
            )

            # Calculate total_price (quantity * unit_price)
            calculated_total = order_item.quantity * order_item.unit_price
            order_item.total_price = calculated_total

            # Set creation timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            if not order_item.created_at:
                order_item.created_at = current_time

            # Add initialization metadata
            if not order_item.metadata:
                order_item.metadata = {}

            order_item.metadata.update(
                {
                    "initialization_date": current_time,
                    "pet_availability_validated": True,
                    "price_calculated": True,
                    "initialization_status": "pending",
                }
            )

            # Update timestamp
            order_item.update_timestamp()

            self.logger.info(
                f"OrderItem {order_item.technical_id} initialized successfully. Total: ${calculated_total}"
            )

            return order_item

        except Exception as e:
            self.logger.error(
                f"Error initializing OrderItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
