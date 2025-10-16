"""
CartTotalsProcessor for Cyoda OMS Application

Handles cart totals calculation and recalculation when items are added,
removed, or updated as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.cart.version_1.cart import Cart
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CartTotalsProcessor(CyodaProcessor):
    """
    Processor for Cart that handles totals calculation and recalculation.
    Ensures cart totals are always accurate when items are modified.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CartTotalsProcessor",
            description="Processes Cart totals calculation and recalculation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Cart to recalculate totals.

        Args:
            entity: The Cart entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed cart with updated totals
        """
        try:
            self.logger.info(
                f"Processing Cart totals for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Cart for type-safe operations
            cart = cast_entity(entity, Cart)

            # Recalculate totals based on current line items
            total_items = 0
            grand_total = 0.0

            for line in cart.lines:
                qty = line.get("qty", 0)
                price = line.get("price", 0.0)

                total_items += qty
                grand_total += price * qty

            # Update cart totals
            cart.totalItems = total_items
            cart.grandTotal = round(grand_total, 2)

            # Update timestamp
            cart.update_timestamp()

            self.logger.info(
                f"Cart {cart.technical_id} totals updated: {total_items} items, ${cart.grandTotal:.2f} total"
            )

            return cart

        except Exception as e:
            self.logger.error(
                f"Error processing cart totals for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
