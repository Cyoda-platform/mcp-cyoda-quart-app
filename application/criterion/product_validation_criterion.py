"""
ProductValidationCriterion for Pet Store Performance Analysis System

Validates that a Product entity meets all required business rules before it can
proceed to the analysis stage as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.product.version_1.product import Product


class ProductValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Product entity that checks all business rules
    before the entity can proceed to performance analysis stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductValidationCriterion",
            description="Validates Product business rules and data consistency for Pet Store analysis",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Product entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Product)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating Product entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Validate required fields
            if not self._validate_required_fields(product):
                return False

            # Validate business logic
            if not self._validate_business_logic(product):
                return False

            # Validate data consistency
            if not self._validate_data_consistency(product):
                return False

            self.logger.info(
                f"Product entity {product.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating Product entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, product: Product) -> bool:
        """
        Validate that all required fields are present and valid.

        Args:
            product: The Product entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate name
        if not product.name or len(product.name.strip()) == 0:
            self.logger.warning(
                f"Product {product.technical_id} has invalid name: '{product.name}'"
            )
            return False

        if len(product.name) > 200:
            self.logger.warning(
                f"Product {product.technical_id} name too long: {len(product.name)} characters"
            )
            return False

        # Validate status
        if product.status not in Product.ALLOWED_STATUSES:
            self.logger.warning(
                f"Product {product.technical_id} has invalid status: {product.status}"
            )
            return False

        return True

    def _validate_business_logic(self, product: Product) -> bool:
        """
        Validate business logic rules.

        Args:
            product: The Product entity to validate

        Returns:
            True if business logic is valid, False otherwise
        """
        # If sales_volume > 0, revenue should also be > 0
        if product.sales_volume and product.sales_volume > 0:
            if not product.revenue or product.revenue <= 0:
                self.logger.warning(
                    f"Product {product.technical_id} has sales volume but no revenue"
                )
                return False

        # Performance score should be between 0 and 100 if set
        if product.performance_score is not None:
            if product.performance_score < 0 or product.performance_score > 100:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid performance score: {product.performance_score}"
                )
                return False

        # Trend indicator should be valid if set
        if product.trend_indicator and product.trend_indicator not in Product.ALLOWED_TRENDS:
            self.logger.warning(
                f"Product {product.technical_id} has invalid trend indicator: {product.trend_indicator}"
            )
            return False

        return True

    def _validate_data_consistency(self, product: Product) -> bool:
        """
        Validate data consistency rules.

        Args:
            product: The Product entity to validate

        Returns:
            True if data is consistent, False otherwise
        """
        # If product is sold, it should have some sales metrics
        if product.status == "sold":
            if not product.sales_volume or product.sales_volume <= 0:
                self.logger.warning(
                    f"Product {product.technical_id} is marked as sold but has no sales volume"
                )
                # This is a warning, not a failure - data might be incomplete
                
        # If inventory count is negative, that's invalid
        if product.inventory_count is not None and product.inventory_count < 0:
            self.logger.warning(
                f"Product {product.technical_id} has negative inventory count: {product.inventory_count}"
            )
            return False

        # If price is set, it should be positive
        if product.price is not None and product.price <= 0:
            self.logger.warning(
                f"Product {product.technical_id} has invalid price: {product.price}"
            )
            return False

        return True
