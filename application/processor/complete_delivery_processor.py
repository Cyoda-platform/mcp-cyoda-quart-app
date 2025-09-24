"""
CompleteDeliveryProcessor for Purrfect Pets API

Handles the completion of order delivery when orders transition from approved to delivered,
marking orders as complete and updating pet status as specified in the Order workflow.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.order.version_1.order import Order
from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class CompleteDeliveryProcessor(CyodaProcessor):
    """
    Processor for completing Order delivery when they transition from approved to delivered.
    Marks order as complete and updates related pet status to sold.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CompleteDeliveryProcessor",
            description="Complete order delivery and update pet status to sold",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity for delivery completion.

        Args:
            entity: The Order entity to complete delivery for (must be in 'approved' state)
            **kwargs: Additional processing parameters

        Returns:
            The delivered order entity marked as complete
        """
        try:
            self.logger.info(
                f"Completing delivery for Order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Set delivery completion details
            self._set_delivery_details(order)

            # Update pet status to sold
            await self._update_pet_status_to_sold(order)

            # Send notification
            self._send_notification(order)

            # Log delivery completion
            self.logger.info(
                f"Order {order.technical_id} delivery completed successfully"
            )

            return order

        except Exception as e:
            self.logger.error(
                f"Error completing delivery for order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _set_delivery_details(self, order: Order) -> None:
        """
        Set delivery completion timestamp and mark order as complete.

        Args:
            order: The Order entity to set delivery details for
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Set delivery timestamp
        order.deliveredAt = current_timestamp

        # Mark order as complete
        order.complete = True

        # Update timestamp
        order.update_timestamp()

        self.logger.debug(
            f"Delivery details set for order: deliveredAt={order.deliveredAt}, complete={order.complete}"
        )

    async def _update_pet_status_to_sold(self, order: Order) -> None:
        """
        Update the pet status to sold.

        Args:
            order: The Order entity containing the pet to update
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
                self.logger.warning(
                    f"Pet with ID {order.petId} not found for status update"
                )
                return

            pet = cast_entity(pet_response.data, Pet)

            # Check if pet is in the right state for sale completion
            if pet.state != "pending":
                self.logger.warning(
                    f"Pet {order.petId} is not in pending state (current: {pet.state}). "
                    "Cannot complete sale transition."
                )
                return

            # Trigger the pet sale completion transition
            await entity_service.execute_transition(
                entity_id=order.petId,
                transition="complete_sale",
                entity_class=Pet.ENTITY_NAME,
                entity_version=str(Pet.ENTITY_VERSION),
            )

            self.logger.info(f"Pet {order.petId} status updated to sold")

        except Exception as e:
            self.logger.error(f"Failed to update pet status to sold: {str(e)}")
            # Don't raise the exception as the order delivery is still complete
            # The pet status update is a secondary operation

    def _send_notification(self, order: Order) -> None:
        """
        Send notification about completed delivery (simulated).

        Args:
            order: The Order entity that was delivered
        """
        # In a real implementation, this would send actual notifications
        self.logger.info(
            f"NOTIFICATION: Order {order.technical_id} has been delivered successfully. "
            f"Delivery completed at {order.deliveredAt}. "
            f"Tracking number: {order.trackingNumber}"
        )

        # Could integrate with notification services:
        # - Delivery confirmation email
        # - SMS delivery notifications
        # - Push notifications
        # - Update customer order history
        # - Trigger customer satisfaction surveys
        # - Update analytics and reporting systems
        # - Generate delivery receipts
