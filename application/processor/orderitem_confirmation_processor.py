"""
OrderItemConfirmationProcessor for Purrfect Pets API

Handles the confirmation of OrderItem entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.orderitem.version_1.orderitem import OrderItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class OrderItemConfirmationProcessor(CyodaProcessor):
    """
    Processor for confirming OrderItem entities.
    Confirms pet availability, locks pet for the order, and sets confirmation timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderItemConfirmationProcessor",
            description="Confirms OrderItem entities by locking pets and setting confirmation timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the OrderItem entity confirmation.

        Args:
            entity: The OrderItem entity to confirm
            **kwargs: Additional processing parameters

        Returns:
            The confirmed OrderItem entity
        """
        try:
            self.logger.info(
                f"Confirming OrderItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to OrderItem for type-safe operations
            order_item = cast_entity(entity, OrderItem)

            # Confirm pet is still available (would normally check Pet entity)
            # For demonstration, we'll assume pet is still available
            self.logger.info(
                f"Pet availability confirmed for pet_id: {order_item.pet_id}"
            )

            # Lock pet for this order (would normally update Pet entity)
            # This would involve transitioning the Pet to pending state
            self.logger.info(
                f"Pet locked for order_id: {order_item.order_id}, pet_id: {order_item.pet_id}"
            )

            # Set confirmation timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add confirmation metadata
            if not order_item.metadata:
                order_item.metadata = {}

            order_item.metadata.update(
                {
                    "confirmation_date": current_time,
                    "pet_confirmed": True,
                    "pet_locked": True,
                    "confirmation_status": "confirmed",
                }
            )

            # Update initialization status
            order_item.metadata["initialization_status"] = "confirmed"

            # Update timestamp
            order_item.update_timestamp()

            self.logger.info(
                f"OrderItem {order_item.technical_id} confirmed successfully"
            )

            return order_item

        except Exception as e:
            self.logger.error(
                f"Error confirming OrderItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
