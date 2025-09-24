"""
CreateOrderProcessor for Purrfect Pets API

Handles the creation and initialization of new orders, validating pet availability,
calculating totals, and setting up order details as specified in the Order workflow.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from application.entity.order.version_1.order import Order
from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class CreateOrderProcessor(CyodaProcessor):
    """
    Processor for creating Order entities when they transition from initial_state to placed.
    Validates pet availability, calculates totals, and sets up order details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreateOrderProcessor",
            description="Create and validate new order with pet availability check",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity for creation.

        Args:
            entity: The Order entity to create (must be in 'initial_state')
            **kwargs: Additional processing parameters

        Returns:
            The created order entity ready for approval
        """
        try:
            self.logger.info(
                f"Creating Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Validate pet availability
            await self._validate_pet_availability(order)

            # Calculate total amount
            await self._calculate_total_amount(order)

            # Set order details
            self._set_order_details(order)

            # Reserve pet (simulated)
            await self._reserve_pet(order)

            # Log order creation completion
            self.logger.info(
                f"Order {order.technical_id} created successfully for pet {order.petId}"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error creating order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_pet_availability(self, order: Order) -> None:
        """
        Validate that the pet is available for ordering.

        Args:
            order: The Order entity to validate

        Raises:
            ValueError: If pet is not available
        """
        entity_service = get_entity_service()

        try:
            # Get the pet entity
            pet_response = await entity_service.get_by_id(
                entity_id=order.petId,
                entity_class=Pet.ENTITY_NAME,
                entity_version=str(Pet.ENTITY_VERSION),
            )

            if not pet_response:
                raise ValueError(f"Pet with ID {order.petId} not found")

            pet = cast_entity(pet_response.data, Pet)

            # Check if pet is available
            if not pet.is_available():
                raise ValueError(
                    f"Pet {order.petId} is not available for ordering (current state: {pet.state})"
                )

            self.logger.debug(f"Pet {order.petId} is available for ordering")

        except Exception as e:
            self.logger.error(f"Failed to validate pet availability: {str(e)}")
            raise

    async def _calculate_total_amount(self, order: Order) -> None:
        """
        Calculate the total amount for the order.

        Args:
            order: The Order entity to calculate total for
        """
        entity_service = get_entity_service()

        try:
            # Get the pet to calculate price
            pet_response = await entity_service.get_by_id(
                entity_id=order.petId,
                entity_class=Pet.ENTITY_NAME,
                entity_version=str(Pet.ENTITY_VERSION),
            )

            if pet_response:
                pet = cast_entity(pet_response.data, Pet)
                pet_price = pet.price if pet.price is not None else 0.0

                # Calculate total (price * quantity)
                order.totalAmount = pet_price * order.quantity

                self.logger.debug(
                    f"Calculated total amount for order: ${order.totalAmount} "
                    f"(${pet_price} x {order.quantity})"
                )
            else:
                # Fallback if pet not found
                order.totalAmount = 0.0
                self.logger.warning(
                    f"Could not find pet {order.petId} for price calculation"
                )

        except Exception as e:
            self.logger.error(f"Failed to calculate total amount: {str(e)}")
            # Set default total amount
            order.totalAmount = 0.0

    def _set_order_details(self, order: Order) -> None:
        """
        Set order creation details and timestamps.

        Args:
            order: The Order entity to set details for
        """
        current_time = datetime.now(timezone.utc)
        current_timestamp = current_time.isoformat().replace("+00:00", "Z")

        # Set order date
        order.orderDate = current_timestamp

        # Set estimated delivery (7 days from now)
        estimated_delivery = current_time + timedelta(days=7)
        order.estimatedDelivery = estimated_delivery.isoformat().replace("+00:00", "Z")

        # Set default shipping date if not provided
        if not order.shipDate:
            # Default ship date is 2 days from now
            ship_date = current_time + timedelta(days=2)
            order.shipDate = ship_date.isoformat().replace("+00:00", "Z")

        # Update timestamp
        order.update_timestamp()

        self.logger.debug(
            f"Order details set: orderDate={order.orderDate}, "
            f"estimatedDelivery={order.estimatedDelivery}, shipDate={order.shipDate}"
        )

    async def _reserve_pet(self, order: Order) -> None:
        """
        Reserve the pet for this order (simulated).

        Args:
            order: The Order entity to reserve pet for
        """
        # In a real implementation, this would trigger the pet reservation
        # For now, we just log the reservation
        self.logger.info(
            f"RESERVATION: Pet {order.petId} reserved for order {order.technical_id}"
        )

        # Could integrate with pet management:
        # - Trigger pet state transition to 'pending'
        # - Update pet reservation details
        # - Set reservation expiry based on order processing time
