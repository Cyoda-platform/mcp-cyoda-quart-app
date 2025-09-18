"""
DeliverOrderProcessor for Cyoda Client Application

Handles the delivery of Order instances when they are delivered to customers.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.order.version_1.order import Order


class DeliverOrderProcessor(CyodaProcessor):
    """
    Processor for delivering Order entities when they are delivered to customers.
    Sets delivered date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DeliverOrderProcessor",
            description="Delivers Order instances by setting delivered date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Deliver the Order entity according to functional requirements.

        Args:
            entity: The Order entity to deliver
            **kwargs: Additional processing parameters

        Returns:
            The delivered order with delivered date set
        """
        try:
            self.logger.info(
                f"Delivering Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Set delivered date and update timestamp
            order.set_delivered_date()

            self.logger.info(
                f"Order {order.technical_id} delivered successfully"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error delivering order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
