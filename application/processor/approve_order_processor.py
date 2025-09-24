"""
ApproveOrderProcessor for Purrfect Pets API

Handles the approval of orders when they transition from placed to approved,
processing payment and setting up shipping details as specified in the Order workflow.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ApproveOrderProcessor(CyodaProcessor):
    """
    Processor for approving Order entities when they transition from placed to approved.
    Processes payment, generates tracking number, and sets up shipping details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApproveOrderProcessor",
            description="Process payment and approve order for shipping",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity for approval.

        Args:
            entity: The Order entity to approve (must be in 'placed' state)
            **kwargs: Additional processing parameters

        Returns:
            The approved order entity ready for shipping
        """
        try:
            self.logger.info(
                f"Approving Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Process payment
            await self._process_payment(order)

            # Set approval details
            self._set_approval_details(order)

            # Generate tracking number
            self._generate_tracking_number(order)

            # Send notification
            self._send_notification(order)

            # Log approval completion
            self.logger.info(
                f"Order {order.technical_id} approved successfully with tracking {order.trackingNumber}"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error approving order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _process_payment(self, order: Order) -> None:
        """
        Process payment for the order (simulated).

        Args:
            order: The Order entity to process payment for

        Raises:
            ValueError: If payment processing fails
        """
        # In a real implementation, this would integrate with payment processors
        # For now, we simulate payment processing

        if not order.totalAmount or order.totalAmount <= 0:
            raise ValueError("Invalid order total amount for payment processing")

        # Simulate payment processing
        self.logger.info(
            f"PAYMENT PROCESSING: Processing payment of ${order.totalAmount} "
            f"for user {order.userId} on order {order.technical_id}"
        )

        # Simulate payment validation
        if order.totalAmount > 10000:  # Arbitrary limit for demo
            raise ValueError("Payment amount exceeds processing limit")

        self.logger.info(f"Payment of ${order.totalAmount} processed successfully")

        # Could integrate with payment services:
        # - Stripe, PayPal, Square, etc.
        # - Validate payment methods
        # - Process charges
        # - Handle payment failures and retries
        # - Store payment transaction details

    def _set_approval_details(self, order: Order) -> None:
        """
        Set order approval timestamp and details.

        Args:
            order: The Order entity to set approval details for
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Set approval timestamp
        order.approvedAt = current_timestamp

        # Update timestamp
        order.update_timestamp()

        self.logger.debug(
            f"Approval details set for order: approvedAt={order.approvedAt}"
        )

    def _generate_tracking_number(self, order: Order) -> None:
        """
        Generate a tracking number for the order.

        Args:
            order: The Order entity to generate tracking number for
        """
        # Generate a simple tracking number
        # In a real implementation, this would integrate with shipping providers
        tracking_prefix = "PP"  # Purrfect Pets prefix
        tracking_suffix = str(uuid.uuid4()).replace("-", "").upper()[:12]
        order.trackingNumber = f"{tracking_prefix}{tracking_suffix}"

        self.logger.debug(f"Generated tracking number: {order.trackingNumber}")

        # Could integrate with shipping providers:
        # - UPS, FedEx, USPS, DHL APIs
        # - Generate real tracking numbers
        # - Schedule pickup/delivery
        # - Calculate shipping costs
        # - Print shipping labels

    def _send_notification(self, order: Order) -> None:
        """
        Send notification about order approval (simulated).

        Args:
            order: The Order entity that was approved
        """
        # In a real implementation, this would send actual notifications
        self.logger.info(
            f"NOTIFICATION: Order {order.technical_id} has been approved and is ready for shipping. "
            f"Tracking number: {order.trackingNumber}. "
            f"Estimated delivery: {order.estimatedDelivery}"
        )

        # Could integrate with notification services:
        # - Email confirmation with tracking details
        # - SMS notifications
        # - Push notifications
        # - Update customer portal
        # - Webhook notifications to external systems
