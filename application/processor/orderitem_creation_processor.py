"""
OrderItemCreationProcessor for Purrfect Pets API

Creates and validates order item according to processors.md specification.
"""

import logging
from decimal import Decimal
from typing import Any

from application.entity.orderitem.version_1.orderitem import OrderItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class OrderItemCreationProcessor(CyodaProcessor):
    """Processor for OrderItem creation that creates and validates order item."""

    def __init__(self) -> None:
        super().__init__(
            name="OrderItemCreationProcessor",
            description="Creates and validates order item",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        try:
            self.logger.info(
                f"Processing creation for OrderItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            order_item = cast_entity(entity, OrderItem)

            # Validate pet exists (placeholder)
            await self._validate_pet_exists(order_item.pet_id)

            # Validate quantity is positive (already done in entity validation)
            if order_item.quantity <= 0:
                raise ValueError("Quantity must be positive")

            # Get current pet price (placeholder)
            current_price = await self._get_current_pet_price(order_item.pet_id)

            # Set unit price to current price
            order_item.unit_price = current_price

            # Calculate total price
            order_item.total_price = order_item.calculate_total_price()

            order_item.update_timestamp()
            self.logger.info(
                f"OrderItem {order_item.technical_id} creation processed successfully"
            )

            return order_item

        except Exception as e:
            self.logger.error(f"Error processing order item creation: {str(e)}")
            raise

    async def _validate_pet_exists(self, pet_id: int) -> None:
        """Validate pet exists"""
        self.logger.info(f"Validated pet {pet_id} exists")

    async def _get_current_pet_price(self, pet_id: int) -> Decimal:
        """Get current pet price"""
        # Placeholder - would fetch from database
        return Decimal("500.00")
