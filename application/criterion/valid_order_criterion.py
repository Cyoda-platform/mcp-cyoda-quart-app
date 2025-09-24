"""
ValidOrderCriterion for Purrfect Pets API

Validates that an Order entity meets all required business rules before it can
proceed to approval as specified in the Order workflow requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.order.version_1.order import Order


class ValidOrderCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Order entities that checks all business rules
    before the entity can proceed to approval.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidOrderCriterion",
            description="Validates Order business rules and data consistency before approval",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the order entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Order)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating order entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Validate required fields
            if not self._validate_required_fields(order):
                return False

            # Validate business rules
            if not self._validate_business_rules(order):
                return False

            # Validate data consistency
            if not self._validate_data_consistency(order):
                return False

            self.logger.info(
                f"Order entity {order.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating order entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, order: Order) -> bool:
        """
        Validate that all required fields are present and valid.

        Args:
            order: The Order entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate pet ID
        if not order.petId or len(order.petId.strip()) == 0:
            self.logger.warning(
                f"Order {order.technical_id} has invalid petId: '{order.petId}'"
            )
            return False

        # Validate user ID
        if not order.userId or len(order.userId.strip()) == 0:
            self.logger.warning(
                f"Order {order.technical_id} has invalid userId: '{order.userId}'"
            )
            return False

        # Validate quantity
        if order.quantity <= 0:
            self.logger.warning(
                f"Order {order.technical_id} has invalid quantity: {order.quantity}"
            )
            return False

        # Validate total amount
        if order.totalAmount is None or order.totalAmount <= 0:
            self.logger.warning(
                f"Order {order.technical_id} has invalid totalAmount: {order.totalAmount}"
            )
            return False

        self.logger.debug(f"Required fields validated for order {order.technical_id}")
        return True

    def _validate_business_rules(self, order: Order) -> bool:
        """
        Validate business rules for the order.

        Args:
            order: The Order entity to validate

        Returns:
            True if business rules are satisfied, False otherwise
        """
        # Validate quantity limits
        if order.quantity > 10:  # Business rule: max 10 pets per order
            self.logger.warning(
                f"Order {order.technical_id} exceeds maximum quantity limit: {order.quantity}"
            )
            return False

        # Validate total amount is reasonable
        if order.totalAmount and order.totalAmount > 100000:  # Business rule: max $100k per order
            self.logger.warning(
                f"Order {order.technical_id} exceeds maximum amount limit: ${order.totalAmount}"
            )
            return False

        # Validate shipping address if provided
        if order.shippingAddress:
            if not self._validate_shipping_address(order.shippingAddress):
                self.logger.warning(
                    f"Order {order.technical_id} has invalid shipping address"
                )
                return False

        self.logger.debug(f"Business rules validated for order {order.technical_id}")
        return True

    def _validate_shipping_address(self, address: dict) -> bool:
        """
        Validate shipping address structure and content.

        Args:
            address: The shipping address dictionary to validate

        Returns:
            True if address is valid, False otherwise
        """
        required_fields = ["street", "city", "state", "zipCode"]
        
        for field in required_fields:
            if field not in address or not address[field] or len(str(address[field]).strip()) == 0:
                return False

        # Validate zip code format (basic validation)
        zip_code = str(address["zipCode"]).strip()
        if len(zip_code) < 5 or len(zip_code) > 10:
            return False

        return True

    def _validate_data_consistency(self, order: Order) -> bool:
        """
        Validate data consistency and state-specific requirements.

        Args:
            order: The Order entity to validate

        Returns:
            True if data is consistent, False otherwise
        """
        # For orders being approved, ensure all required data is present
        if order.state == "placed":
            # Orders should have order date set
            if not order.orderDate:
                self.logger.warning(
                    f"Order {order.technical_id} is placed but has no order date"
                )
                # Don't fail validation as this might be set by the processor
                pass

            # Orders should have estimated delivery
            if not order.estimatedDelivery:
                self.logger.warning(
                    f"Order {order.technical_id} is placed but has no estimated delivery"
                )
                # Don't fail validation as this might be set by the processor
                pass

        # For approved orders, check approval details
        if order.state == "approved":
            if not order.approvedAt:
                self.logger.warning(
                    f"Order {order.technical_id} is approved but has no approval timestamp"
                )
                # Don't fail validation as this might be set by the processor
                pass

            if not order.trackingNumber:
                self.logger.warning(
                    f"Order {order.technical_id} is approved but has no tracking number"
                )
                # Don't fail validation as this might be set by the processor
                pass

        # For delivered orders, check delivery details
        if order.state == "delivered":
            if not order.deliveredAt:
                self.logger.warning(
                    f"Order {order.technical_id} is delivered but has no delivery timestamp"
                )
                # Don't fail validation as this might be set by the processor
                pass

            if not order.complete:
                self.logger.warning(
                    f"Order {order.technical_id} is delivered but not marked as complete"
                )
                # Don't fail validation as this might be set by the processor
                pass

        self.logger.debug(f"Data consistency validated for order {order.technical_id}")
        return True
