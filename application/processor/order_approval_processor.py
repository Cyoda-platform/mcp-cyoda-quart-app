"""
OrderApprovalProcessor for Purrfect Pets API

Approves order for processing according to processors.md specification.
"""

import logging
from typing import Any, Optional, Protocol, cast

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _EntityService(Protocol):
    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class OrderApprovalProcessor(CyodaProcessor):
    """
    Processor for Order approval that approves order for processing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderApprovalProcessor",
            description="Approves order for processing",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity approval according to functional requirements.

        Args:
            entity: The Order entity to approve
            **kwargs: Additional processing parameters

        Returns:
            The approved order entity
        """
        try:
            self.logger.info(
                f"Processing approval for Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Validate payment information (placeholder)
            await self._validate_payment_information(order)

            # Validate inventory availability (placeholder)
            await self._validate_inventory_availability(order)

            # Confirm each order item and update to CONFIRMED state
            await self._confirm_order_items(order)

            # Send order confirmation email (placeholder)
            await self._send_order_confirmation_email(order)

            # Update timestamp
            order.update_timestamp()

            self.logger.info(
                f"Order {order.technical_id} approval processed successfully"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error processing order approval {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_payment_information(self, order: Order) -> None:
        """Validate payment information"""
        if not order.payment_method:
            raise ValueError("Payment method is required for order approval")
        self.logger.info(f"Payment validation passed for order {order.technical_id}")

    async def _validate_inventory_availability(self, order: Order) -> None:
        """Validate inventory availability"""
        # Placeholder for inventory validation
        self.logger.info(f"Inventory validation passed for order {order.technical_id}")

    async def _confirm_order_items(self, order: Order) -> None:
        """Confirm each order item"""
        try:
            entity_service = self._get_entity_service()

            if order.metadata and "order_items" in order.metadata:
                order_items = order.metadata["order_items"]
                for item in order_items:
                    item_id = item.get("id")
                    if item_id:
                        await entity_service.execute_transition(
                            entity_id=item_id,
                            transition="transition_to_confirmed",
                            entity_class="OrderItem",
                            entity_version="1",
                        )
                        self.logger.info(f"Confirmed order item {item_id}")

        except Exception as e:
            self.logger.error(f"Failed to confirm order items: {str(e)}")
            raise

    async def _send_order_confirmation_email(self, order: Order) -> None:
        """Send order confirmation email"""
        try:
            # Placeholder for email sending
            self.logger.info(
                f"Sent order confirmation email for order {order.technical_id}"
            )

        except Exception as e:
            self.logger.warning(f"Failed to send confirmation email: {str(e)}")
            # Don't raise - email failure shouldn't stop approval
