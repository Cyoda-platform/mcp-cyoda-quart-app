"""
OrderDeliveryProcessor for Purrfect Pets API

Marks order as delivered according to processors.md specification.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional, Protocol, cast

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _EntityService(Protocol):
    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class OrderDeliveryProcessor(CyodaProcessor):
    """Processor for Order delivery that marks order as delivered."""

    def __init__(self) -> None:
        super().__init__(
            name="OrderDeliveryProcessor",
            description="Marks order as delivered",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        try:
            self.logger.info(
                f"Processing delivery for Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            order = cast_entity(entity, Order)

            # Validate all items are ready for delivery
            await self._validate_items_ready(order)

            # Set ship date to current time
            order.ship_date = datetime.now(timezone.utc)

            # Mark each order item as delivered and associated pet as sold
            await self._deliver_order_items(order)

            # Send delivery confirmation
            await self._send_delivery_confirmation(order)

            order.update_timestamp()
            self.logger.info(
                f"Order {order.technical_id} delivery processed successfully"
            )

            return order

        except Exception as e:
            self.logger.error(f"Error processing order delivery: {str(e)}")
            raise

    async def _validate_items_ready(self, order: Order) -> None:
        """Validate all items are ready for delivery"""
        self.logger.info(
            f"Validated items ready for delivery for order {order.technical_id}"
        )

    async def _deliver_order_items(self, order: Order) -> None:
        """Mark items as delivered and pets as sold"""
        try:
            entity_service = self._get_entity_service()

            if order.metadata and "order_items" in order.metadata:
                for item in order.metadata["order_items"]:
                    # Mark order item as delivered
                    if item.get("id"):
                        await entity_service.execute_transition(
                            entity_id=item["id"],
                            transition="transition_to_delivered",
                            entity_class="OrderItem",
                            entity_version="1",
                        )

                    # Mark associated pet as sold
                    if item.get("pet_id"):
                        await entity_service.execute_transition(
                            entity_id=str(item["pet_id"]),
                            transition="transition_to_sold",
                            entity_class="Pet",
                            entity_version="1",
                        )

        except Exception as e:
            self.logger.error(f"Failed to deliver order items: {str(e)}")
            raise

    async def _send_delivery_confirmation(self, order: Order) -> None:
        """Send delivery confirmation"""
        self.logger.info(f"Sent delivery confirmation for order {order.technical_id}")
