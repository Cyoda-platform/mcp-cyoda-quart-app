"""
OrderShippingProcessor for Purrfect Pets API

Handles the shipping of Order entities.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class OrderShippingProcessor(CyodaProcessor):
    """
    Processor for shipping Order entities.
    Generates shipping label, updates shipping address, and sends tracking information.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderShippingProcessor",
            description="Ships Order entities by generating labels and sending tracking information",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity shipping.

        Args:
            entity: The Order entity to ship
            **kwargs: Additional processing parameters (may include updated_shipping_address)

        Returns:
            The shipped Order entity
        """
        try:
            self.logger.info(
                f"Shipping Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Generate shipping label
            shipping_label_id = f"SHIP-{uuid.uuid4().hex[:8].upper()}"
            tracking_number = f"TRK-{uuid.uuid4().hex[:12].upper()}"

            # Update shipping address if provided
            updated_address = kwargs.get("updated_shipping_address")
            if updated_address:
                order.shipping_address = updated_address
                self.logger.info(
                    f"Shipping address updated for Order {order.technical_id}"
                )

            # Set ship_date
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            order.ship_date = current_time

            # Add shipping metadata
            if not order.metadata:
                order.metadata = {}

            order.metadata.update(
                {
                    "shipping_date": current_time,
                    "shipping_label_id": shipping_label_id,
                    "tracking_number": tracking_number,
                    "shipping_status": "shipped",
                    "tracking_info_sent": True,
                }
            )

            # Update timestamp
            order.update_timestamp()

            # Send tracking information (would normally integrate with email service)
            self.logger.info(
                f"Tracking information sent for Order {order.technical_id}: {tracking_number}"
            )

            self.logger.info(
                f"Order {order.technical_id} shipped successfully with tracking number {tracking_number}"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error shipping Order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
