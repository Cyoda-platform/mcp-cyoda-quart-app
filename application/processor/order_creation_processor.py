"""
OrderCreationProcessor for Purrfect Pets API

Creates and validates new order according to processors.md specification.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional, Protocol, cast

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _HasId(Protocol):
    id: str


class _HasMetadata(Protocol):
    metadata: _HasId


class _EntityService(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Dict[str, Any]]: ...

    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _HasMetadata: ...

    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class OrderCreationProcessor(CyodaProcessor):
    """
    Processor for Order creation that creates and validates new order.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderCreationProcessor",
            description="Creates and validates new order",
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
        Process the Order entity creation according to functional requirements.

        Args:
            entity: The Order entity to create
            **kwargs: Additional processing parameters including order_items

        Returns:
            The created order entity
        """
        try:
            self.logger.info(
                f"Processing creation for Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Validate user exists and is active
            await self._validate_user(order.user_id)

            # Get order items from kwargs
            order_items = kwargs.get("order_items", [])
            if not order_items or len(order_items) == 0:
                raise ValueError("Order must have at least one item")

            # Process each order item
            total_amount = Decimal("0.00")
            created_items = []

            for item_data in order_items:
                # Validate pet exists and is available
                pet_id = item_data.get("pet_id")
                quantity = item_data.get("quantity", 1)

                pet_data = await self._validate_pet_availability(pet_id)

                # Calculate item total price
                unit_price = Decimal(str(pet_data.get("price", 0)))
                item_total = unit_price * quantity
                total_amount += item_total

                # Create order item entity
                order_item = await self._create_order_item(
                    order, pet_id, quantity, unit_price, item_total
                )
                created_items.append(order_item)

                # Reserve pet (trigger Pet to PENDING)
                await self._reserve_pet(pet_id, order.technical_id)

            # Calculate order total amount
            order.total_amount = total_amount

            # Set order date to current time
            order.order_date = datetime.now(timezone.utc)

            # Store created items in metadata
            if order.metadata is None:
                order.metadata = {}
            order.metadata["order_items"] = created_items
            order.metadata["items_count"] = len(created_items)

            # Update timestamp
            order.update_timestamp()

            self.logger.info(
                f"Order {order.technical_id} creation processed successfully with {len(created_items)} items"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error processing order creation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_user(self, user_id: int) -> None:
        """Validate user exists and is active"""
        try:
            entity_service = self._get_entity_service()
            user_data = await entity_service.get_by_id(
                entity_id=str(user_id), entity_class="User", entity_version="1"
            )

            if not user_data:
                raise ValueError(f"User with ID {user_id} not found")

            if user_data.get("state") != "active":
                raise ValueError(f"User {user_id} is not active")

        except Exception as e:
            self.logger.error(f"User validation failed: {str(e)}")
            raise

    async def _validate_pet_availability(self, pet_id: int) -> Dict[str, Any]:
        """Validate pet exists and is available"""
        try:
            entity_service = self._get_entity_service()
            pet_data = await entity_service.get_by_id(
                entity_id=str(pet_id), entity_class="Pet", entity_version="1"
            )

            if not pet_data:
                raise ValueError(f"Pet with ID {pet_id} not found")

            if pet_data.get("state") != "available":
                raise ValueError(f"Pet {pet_id} is not available")

            return pet_data

        except Exception as e:
            self.logger.error(f"Pet validation failed: {str(e)}")
            raise

    async def _create_order_item(
        self,
        order: Order,
        pet_id: int,
        quantity: int,
        unit_price: Decimal,
        total_price: Decimal,
    ) -> Dict[str, Any]:
        """Create order item entity"""
        try:
            entity_service = self._get_entity_service()

            order_item_data = {
                "orderId": order.technical_id,
                "petId": pet_id,
                "quantity": quantity,
                "unitPrice": float(unit_price),
                "totalPrice": float(total_price),
            }

            response = await entity_service.save(
                entity=order_item_data, entity_class="OrderItem", entity_version="1"
            )

            return {
                "id": response.metadata.id,
                "pet_id": pet_id,
                "quantity": quantity,
                "unit_price": float(unit_price),
                "total_price": float(total_price),
            }

        except Exception as e:
            self.logger.error(f"Failed to create order item: {str(e)}")
            raise

    async def _reserve_pet(self, pet_id: int, order_id: str) -> None:
        """Reserve pet for this order"""
        try:
            entity_service = self._get_entity_service()

            # Trigger pet reservation transition
            await entity_service.execute_transition(
                entity_id=str(pet_id),
                transition="transition_to_pending",
                entity_class="Pet",
                entity_version="1",
            )

            self.logger.info(f"Reserved pet {pet_id} for order {order_id}")

        except Exception as e:
            self.logger.error(f"Failed to reserve pet {pet_id}: {str(e)}")
            raise
