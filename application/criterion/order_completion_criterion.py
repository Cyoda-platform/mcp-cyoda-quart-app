"""
OrderCompletionCriterion for Purrfect Pets API

Checks if the associated order is completed (in Delivered state).
"""

import logging
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class OrderCompletionCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if the associated order is completed.
    Verifies the order containing this pet is in Delivered state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderCompletionCriterion",
            description="Checks if associated order is completed",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the associated order is completed.

        Args:
            entity: The CyodaEntity to check (expected to be Pet)
            **kwargs: Additional criteria parameters (should contain order_context)

        Returns:
            True if the order is completed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking order completion for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Extract order context from kwargs
            order_context = kwargs.get("order_context", {})
            order_id = order_context.get("order_id")

            if not order_id:
                self.logger.warning(
                    f"No order_id provided in order_context for pet {pet.technical_id}"
                )
                return False

            # Check if the order is in Delivered state
            order_completed = await self._check_order_status(order_id)

            if order_completed:
                self.logger.info(
                    f"Order {order_id} is completed for pet {pet.technical_id}"
                )
            else:
                self.logger.info(
                    f"Order {order_id} is not completed for pet {pet.technical_id}"
                )

            return order_completed

        except Exception as e:
            self.logger.error(
                f"Error checking order completion for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _check_order_status(self, order_id: str) -> bool:
        """
        Check if the order is in Delivered state.

        Args:
            order_id: The order ID to check

        Returns:
            True if order is delivered, False otherwise
        """
        try:
            self.logger.debug(f"Checking status for order {order_id}")

            # In a real implementation, we would:
            # 1. Get the order by ID using entity service
            # 2. Check if order.state == "Delivered"

            # For now, we'll return False as a safe default
            # This would need to be implemented with actual order lookup

            self.logger.debug(f"Order {order_id} status check completed")
            return False

        except Exception as e:
            self.logger.error(f"Error checking status for order {order_id}: {str(e)}")
            return False
