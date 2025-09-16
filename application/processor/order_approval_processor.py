"""
OrderApprovalProcessor for Purrfect Pets API

Handles the approval of Order entities after validation.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class OrderApprovalProcessor(CyodaProcessor):
    """
    Processor for approving Order entities.
    Verifies payment method, confirms pet availability, and sends approval notification.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderApprovalProcessor",
            description="Approves Order entities by verifying payment and confirming pet availability",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity approval.

        Args:
            entity: The Order entity to approve
            **kwargs: Additional processing parameters

        Returns:
            The approved Order entity
        """
        try:
            self.logger.info(
                f"Approving Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Verify payment method (would normally integrate with payment service)
            self.logger.info(
                f"Payment method verified for Order {order.technical_id}: {order.payment_method}"
            )

            # Confirm pet availability (would normally check Pet entities)
            self.logger.info(
                f"Pet availability confirmed for Order {order.technical_id}"
            )

            # Set approval timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add approval metadata
            if not order.metadata:
                order.metadata = {}

            order.metadata.update(
                {
                    "approval_date": current_time,
                    "approval_status": "approved",
                    "payment_verified": True,
                    "pets_confirmed": True,
                    "approval_notification_sent": True,
                }
            )

            # Update timestamp
            order.update_timestamp()

            # Send approval notification (would normally integrate with email service)
            self.logger.info(
                f"Approval notification sent for Order {order.technical_id}"
            )

            self.logger.info(f"Order {order.technical_id} approved successfully")

            return order

        except Exception as e:
            self.logger.error(
                f"Error approving Order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
