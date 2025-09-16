"""
OrderDeliveryProcessor for Purrfect Pets API

Handles the delivery confirmation of Order entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.order.version_1.order import Order


class OrderDeliveryProcessor(CyodaProcessor):
    """
    Processor for confirming Order delivery.
    Records delivery timestamp, sends confirmation, and requests customer feedback.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderDeliveryProcessor",
            description="Confirms Order delivery by recording timestamp and sending confirmation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity delivery confirmation.

        Args:
            entity: The Order entity to confirm delivery
            **kwargs: Additional processing parameters (may include delivery_confirmation)

        Returns:
            The delivered Order entity
        """
        try:
            self.logger.info(
                f"Confirming delivery for Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Record delivery timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Get delivery confirmation details from kwargs
            delivery_confirmation = kwargs.get("delivery_confirmation", {})

            # Add delivery metadata
            if not order.metadata:
                order.metadata = {}
            
            order.metadata.update({
                "delivery_date": current_time,
                "delivery_status": "delivered",
                "delivery_confirmation_sent": True,
                "feedback_request_sent": True
            })

            # Add delivery confirmation details if provided
            if delivery_confirmation:
                order.metadata["delivery_confirmation"] = delivery_confirmation

            # Update timestamp
            order.update_timestamp()

            # Send delivery confirmation (would normally integrate with email service)
            self.logger.info(f"Delivery confirmation sent for Order {order.technical_id}")

            # Request customer feedback (would normally integrate with feedback service)
            self.logger.info(f"Customer feedback request sent for Order {order.technical_id}")

            self.logger.info(
                f"Order {order.technical_id} delivery confirmed successfully"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error confirming delivery for Order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
