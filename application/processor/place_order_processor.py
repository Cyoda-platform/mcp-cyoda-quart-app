"""
PlaceOrderProcessor for Cyoda Client Application

Handles the placement of Order instances when they are first created.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.order.version_1.order import Order


class PlaceOrderProcessor(CyodaProcessor):
    """
    Processor for placing Order entities when they are first created.
    Sets placed date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PlaceOrderProcessor",
            description="Places Order instances with placed date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Place the Order entity according to functional requirements.

        Args:
            entity: The Order entity to place
            **kwargs: Additional processing parameters

        Returns:
            The placed order with placed date set
        """
        try:
            self.logger.info(
                f"Placing Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Set placed date and update timestamp
            order.set_placed_date()

            self.logger.info(
                f"Order {order.technical_id} placed successfully"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error placing order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
