"""
ApproveOrderProcessor for Cyoda Client Application

Handles the approval of Order instances when they are approved for processing.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.order.version_1.order import Order


class ApproveOrderProcessor(CyodaProcessor):
    """
    Processor for approving Order entities when they are approved for processing.
    Sets approved date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApproveOrderProcessor",
            description="Approves Order instances by setting approved date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Approve the Order entity according to functional requirements.

        Args:
            entity: The Order entity to approve
            **kwargs: Additional processing parameters

        Returns:
            The approved order with approved date set
        """
        try:
            self.logger.info(
                f"Approving Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Set approved date and update timestamp
            order.set_approved_date()

            self.logger.info(
                f"Order {order.technical_id} approved successfully"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error approving order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
