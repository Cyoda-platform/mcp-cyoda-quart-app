"""
ValidOrderCriterion for Cyoda Client Application

Validates that an Order meets all required business rules before it can
be approved for processing as specified in functional requirements.
"""

from typing import Any

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ValidOrderCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Order that checks all business rules
    before the order can be approved for processing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidOrderCriterion",
            description="Validates Order business rules and data consistency for approval",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the order meets all validation criteria for approval.

        Args:
            entity: The CyodaEntity to validate (expected to be Order)
            **kwargs: Additional criteria parameters

        Returns:
            True if the order meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Validate required fields
            if not order.pet_id or len(order.pet_id.strip()) == 0:
                self.logger.warning(
                    f"Order {order.technical_id} has invalid pet_id: '{order.pet_id}'"
                )
                return False

            if not order.user_id or len(order.user_id.strip()) == 0:
                self.logger.warning(
                    f"Order {order.technical_id} has invalid user_id: '{order.user_id}'"
                )
                return False

            # Validate quantity
            if order.quantity <= 0:
                self.logger.warning(
                    f"Order {order.technical_id} has invalid quantity: {order.quantity}"
                )
                return False

            if order.quantity > 100:
                self.logger.warning(
                    f"Order {order.technical_id} has excessive quantity: {order.quantity}"
                )
                return False

            # Validate total amount if provided
            if order.total_amount is not None and order.total_amount < 0:
                self.logger.warning(
                    f"Order {order.technical_id} has negative total amount: {order.total_amount}"
                )
                return False

            # Business rule: Orders with quantity > 10 require special handling
            if order.quantity > 10 and order.total_amount is None:
                self.logger.warning(
                    f"Order {order.technical_id} with quantity > 10 requires total amount"
                )
                return False

            # Business rule: Orders with high total amount require additional validation
            if order.total_amount is not None and order.total_amount > 10000:
                self.logger.info(
                    f"Order {order.technical_id} has high value: {order.total_amount} - requires manual review"
                )
                # For now, we'll allow high-value orders but log them for review
                # In a real system, this might trigger additional approval workflows

            self.logger.info(
                f"Order {order.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
