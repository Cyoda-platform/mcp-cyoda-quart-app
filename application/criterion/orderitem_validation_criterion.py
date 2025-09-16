"""
OrderItemValidationCriterion for Purrfect Pets API

Validates that an order item meets all requirements before confirmation.
"""

from typing import Any

from application.entity.orderitem.version_1.orderitem import OrderItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class OrderItemValidationCriterion(CyodaCriteriaChecker):
    """
    Criterion for validating OrderItem before confirmation.
    Checks all order item requirements and business rules.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderItemValidationCriterion",
            description="Validates OrderItem before confirmation by checking all requirements",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the order item is valid for confirmation.

        Args:
            entity: The CyodaEntity to validate (expected to be OrderItem)
            **kwargs: Additional criteria parameters

        Returns:
            True if order item is valid for confirmation, False otherwise
        """
        try:
            self.logger.info(
                f"Validating OrderItem {getattr(entity, 'technical_id', '<unknown>')} for confirmation"
            )

            # Cast the entity to OrderItem for type-safe operations
            order_item = cast_entity(entity, OrderItem)

            # Check if order item is in pending state
            if not order_item.is_pending():
                self.logger.warning(
                    f"OrderItem {order_item.technical_id} is not in pending state"
                )
                return False

            # Check pet still exists and is available (would normally check Pet entity)
            if not order_item.metadata:
                self.logger.warning(
                    f"No metadata found for OrderItem {order_item.technical_id}"
                )
                return False

            pet_exists = order_item.metadata.get("pet_exists", False)
            if not pet_exists:
                self.logger.warning(
                    f"Pet does not exist for OrderItem {order_item.technical_id}"
                )
                return False

            pet_available = order_item.metadata.get("pet_available", False)
            if not pet_available:
                self.logger.warning(
                    f"Pet is not available for OrderItem {order_item.technical_id}"
                )
                return False

            # Verify quantity is valid (positive integer)
            if order_item.quantity <= 0:
                self.logger.warning(
                    f"Invalid quantity {order_item.quantity} for OrderItem {order_item.technical_id}"
                )
                return False

            # Validate unit_price matches current pet price (would normally check Pet entity)
            current_pet_price = order_item.metadata.get("current_pet_price")
            if (
                current_pet_price
                and abs(float(current_pet_price) - order_item.unit_price) > 0.01
            ):
                self.logger.warning(
                    f"Unit price ${order_item.unit_price} does not match current pet price ${current_pet_price} for OrderItem {order_item.technical_id}"
                )
                return False

            # Confirm total_price calculation is correct
            expected_total = order_item.quantity * order_item.unit_price
            if abs(order_item.total_price - expected_total) > 0.01:
                self.logger.warning(
                    f"Total price calculation error for OrderItem {order_item.technical_id}: expected ${expected_total}, got ${order_item.total_price}"
                )
                return False

            # Check pet is not already sold (would normally check Pet entity)
            pet_sold = order_item.metadata.get("pet_sold", False)
            if pet_sold:
                self.logger.warning(
                    f"Pet is already sold for OrderItem {order_item.technical_id}"
                )
                return False

            self.logger.info(
                f"OrderItem validation successful for OrderItem {order_item.technical_id}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating OrderItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
