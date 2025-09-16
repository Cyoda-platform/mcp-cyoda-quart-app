"""
OrderValidationCriterion for Purrfect Pets API

Validates that an order meets all requirements before approval.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.order.version_1.order import Order


class OrderValidationCriterion(CyodaCriteriaChecker):
    """
    Criterion for validating Order before approval.
    Checks all order requirements and business rules.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderValidationCriterion",
            description="Validates Order before approval by checking all requirements",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the order is valid for approval.

        Args:
            entity: The CyodaEntity to validate (expected to be Order)
            **kwargs: Additional criteria parameters

        Returns:
            True if order is valid for approval, False otherwise
        """
        try:
            self.logger.info(
                f"Validating Order {getattr(entity, 'technical_id', '<unknown>')} for approval"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Check if order is in placed state
            if not order.is_placed():
                self.logger.warning(
                    f"Order {order.technical_id} is not in placed state"
                )
                return False

            # Check all order items are valid (would normally validate order items)
            # For demonstration, we'll check metadata for order items validation
            if not order.metadata:
                self.logger.warning(f"No metadata found for Order {order.technical_id}")
                return False

            order_items_valid = order.metadata.get("order_items_valid", False)
            if not order_items_valid:
                self.logger.warning(
                    f"Order items are not valid for Order {order.technical_id}"
                )
                return False

            # Verify all pets in order are available
            pets_available = order.metadata.get("pets_available", False)
            if not pets_available:
                self.logger.warning(
                    f"Not all pets are available for Order {order.technical_id}"
                )
                return False

            # Validate shipping address is complete
            if not order.shipping_address or len(order.shipping_address.strip()) == 0:
                self.logger.warning(
                    f"Shipping address is missing for Order {order.technical_id}"
                )
                return False

            if len(order.shipping_address) < 10:  # Basic validation
                self.logger.warning(
                    f"Shipping address is too short for Order {order.technical_id}"
                )
                return False

            # Confirm payment method is provided
            if not order.payment_method or len(order.payment_method.strip()) == 0:
                self.logger.warning(
                    f"Payment method is missing for Order {order.technical_id}"
                )
                return False

            valid_payment_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]
            if order.payment_method not in valid_payment_methods:
                self.logger.warning(
                    f"Invalid payment method '{order.payment_method}' for Order {order.technical_id}"
                )
                return False

            # Check user account is active (would normally check User entity)
            user_active = order.metadata.get("user_active", False)
            if not user_active:
                self.logger.warning(
                    f"User account is not active for Order {order.technical_id}"
                )
                return False

            # Validate total amount calculation is correct
            if order.total_amount <= 0:
                self.logger.warning(
                    f"Invalid total amount ${order.total_amount} for Order {order.technical_id}"
                )
                return False

            # Check if calculated total matches expected total
            calculated_total = order.metadata.get("total_calculated")
            if calculated_total and abs(float(calculated_total) - order.total_amount) > 0.01:
                self.logger.warning(
                    f"Total amount mismatch for Order {order.technical_id}: expected ${calculated_total}, got ${order.total_amount}"
                )
                return False

            self.logger.info(
                f"Order validation successful for Order {order.technical_id}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating Order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
