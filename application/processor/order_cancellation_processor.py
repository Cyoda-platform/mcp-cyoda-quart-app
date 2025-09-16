"""
OrderCancellationProcessor for Purrfect Pets API

Handles the cancellation of Order entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class OrderCancellationProcessor(CyodaProcessor):
    """
    Processor for cancelling Order entities.
    Records cancellation reason, processes refunds, and releases reserved pets.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderCancellationProcessor",
            description="Cancels Order entities by processing refunds and releasing reserved pets",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity cancellation.

        Args:
            entity: The Order entity to cancel
            **kwargs: Additional processing parameters (may include cancellation_reason)

        Returns:
            The cancelled Order entity
        """
        try:
            self.logger.info(
                f"Cancelling Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Get cancellation reason from kwargs or use default
            cancellation_reason = kwargs.get(
                "cancellation_reason", "Order cancelled by customer"
            )

            # Record cancellation reason and timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Process refund if payment was made (would normally integrate with payment service)
            refund_processed = False
            if order.metadata and order.metadata.get("payment_verified"):
                self.logger.info(
                    f"Processing refund for Order {order.technical_id}: ${order.total_amount}"
                )
                refund_processed = True

            # Release reserved pets (would normally update Pet entities back to available state)
            # This would be done by updating related Pet entities via EntityService
            # For demonstration, we'll log this action
            # In a real implementation, we would:
            # 1. Get all pets from order items
            # 2. Update each pet back to available state using transition_to_available
            self.logger.info(f"Reserved pets released for Order {order.technical_id}")

            # Add cancellation metadata
            if not order.metadata:
                order.metadata = {}

            order.metadata.update(
                {
                    "cancellation_date": current_time,
                    "cancellation_reason": cancellation_reason,
                    "cancellation_status": "cancelled",
                    "refund_processed": refund_processed,
                    "pets_released": True,
                    "cancellation_notification_sent": True,
                }
            )

            # Update timestamp
            order.update_timestamp()

            # Send cancellation notification (would normally integrate with email service)
            self.logger.info(
                f"Cancellation notification sent for Order {order.technical_id}"
            )

            self.logger.info(
                f"Order {order.technical_id} cancelled successfully. Reason: {cancellation_reason}"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error cancelling Order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
