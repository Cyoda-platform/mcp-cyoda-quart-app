"""
ProductValidationCriterion for Pet Store Performance Analysis System

Validates that Product entities meet all required business rules and data quality
standards before proceeding to analysis stage as specified in functional requirements.
"""

from typing import Any

from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ProductValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Product entity that checks data quality,
    business rules, and completeness before analysis.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductValidationCriterion",
            description="Validates Product entity data quality and business rules",
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
                f"Validating product {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Validate required fields
            if not self._validate_required_fields(product):
                return False

            # Validate data formats and ranges
            if not self._validate_data_formats(product):
                return False

            # Validate business rules
            if not self._validate_business_rules(product):
                return False

            # Validate data consistency
            if not self._validate_data_consistency(product):
                return False

            self.logger.info(
                f"Product {product.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, product: Product) -> bool:
        """
        Validate that all required fields are present and non-empty.

        Args:
            product: The Product entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate product_id
        if not product.product_id or len(product.product_id.strip()) == 0:
            self.logger.warning(
                f"Product {product.technical_id} has invalid product_id"
            )
            return False

        # Validate name
        if not product.name or len(product.name.strip()) < 3:
            self.logger.warning(
                f"Product {product.technical_id} has invalid name: '{product.name}'"
            )
            return False

        # Validate category
        if product.category not in product.ALLOWED_CATEGORIES:
            self.logger.warning(
                f"Product {product.technical_id} has invalid category: {product.category}"
            )
            return False

        # Validate status
        if product.status not in product.ALLOWED_STATUSES:
            self.logger.warning(
                f"Product {product.technical_id} has invalid status: {product.status}"
            )
            return False

        return True

    def _validate_data_formats(self, product: Product) -> bool:
        """
        Validate data formats and ranges.

        Args:
            product: The Product entity to validate

        Returns:
            True if all data formats are valid, False otherwise
        """
        # Validate price
        if product.price is not None:
            if product.price < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative price: {product.price}"
                )
                return False
            if product.price > 10000:  # Reasonable upper limit
                self.logger.warning(
                    f"Product {product.technical_id} has unrealistic price: {product.price}"
                )
                return False

        # Validate sales volume
        if product.sales_volume is not None:
            if product.sales_volume < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative sales volume: {product.sales_volume}"
                )
                return False

        # Validate inventory level
        if product.inventory_level is not None:
            if product.inventory_level < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative inventory: {product.inventory_level}"
                )
                return False

        # Validate revenue
        if product.revenue is not None:
            if product.revenue < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative revenue: {product.revenue}"
                )
                return False

        # Validate performance score if present
        if product.performance_score is not None:
            if not (0 <= product.performance_score <= 100):
                self.logger.warning(
                    f"Product {product.technical_id} has invalid performance score: {product.performance_score}"
                )
                return False

        # Validate trend indicator if present
        if product.trend_indicator is not None:
            if product.trend_indicator not in product.ALLOWED_TRENDS:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid trend indicator: {product.trend_indicator}"
                )
                return False

        return True

    def _validate_business_rules(self, product: Product) -> bool:
        """
        Validate business logic rules.

        Args:
            product: The Product entity to validate

        Returns:
            True if all business rules are satisfied, False otherwise
        """
        # Rule: Products with status 'sold' should have sales volume > 0
        if product.status == "sold" and (product.sales_volume or 0) == 0:
            self.logger.warning(
                f"Product {product.technical_id} marked as sold but has no sales volume"
            )
            return False

        # Rule: Available products should have inventory > 0
        if product.status == "available" and (product.inventory_level or 0) == 0:
            self.logger.warning(
                f"Product {product.technical_id} marked as available but has no inventory"
            )
            return False

        # Rule: Products with high sales should not have very high inventory (potential data error)
        sales_volume = product.sales_volume or 0
        inventory_level = product.inventory_level or 0
        if sales_volume > 100 and inventory_level > sales_volume * 10:
            self.logger.warning(
                f"Product {product.technical_id} has suspicious inventory/sales ratio: "
                f"Sales: {sales_volume}, Inventory: {inventory_level}"
            )
            return False

        return True

    def _validate_data_consistency(self, product: Product) -> bool:
        """
        Validate data consistency across related fields.

        Args:
            product: The Product entity to validate

        Returns:
            True if data is consistent, False otherwise
        """
        # Check revenue calculation consistency
        if (
            product.price is not None
            and product.sales_volume is not None
            and product.revenue is not None
        ):

            expected_revenue = product.price * product.sales_volume
            actual_revenue = product.revenue

            # Allow for small floating point differences
            if abs(expected_revenue - actual_revenue) > 0.01:
                self.logger.warning(
                    f"Product {product.technical_id} has inconsistent revenue calculation: "
                    f"Expected: {expected_revenue}, Actual: {actual_revenue}"
                )
                return False

        # Check inventory turnover consistency if present
        if (
            product.inventory_turnover_rate is not None
            and product.sales_volume is not None
            and product.inventory_level is not None
            and product.inventory_level > 0
        ):

            expected_turnover = product.sales_volume / product.inventory_level
            actual_turnover = product.inventory_turnover_rate

            # Allow for reasonable difference
            if abs(expected_turnover - actual_turnover) > 0.1:
                self.logger.warning(
                    f"Product {product.technical_id} has inconsistent inventory turnover: "
                    f"Expected: {expected_turnover}, Actual: {actual_turnover}"
                )
                return False

        return True
