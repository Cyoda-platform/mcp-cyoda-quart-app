"""
ProductValidationCriterion for Product Performance Analysis and Reporting System

Validates Product entities to ensure data quality and business rules compliance
before proceeding to performance analysis.
"""

from typing import Any

from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ProductValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Product entity that checks data quality and business rules.

    Validates:
    - Required fields are present and valid
    - Data types and value ranges
    - Business logic constraints
    - API data integrity
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
                f"Validating Product entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Validate required fields
            if not self._validate_required_fields(product):
                return False

            # Validate data types and ranges
            if not self._validate_data_ranges(product):
                return False

            # Validate business rules
            if not self._validate_business_rules(product):
                return False

            # Validate API data integrity
            if not self._validate_api_data(product):
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

        # Validate category
        if not product.category or product.category not in product.ALLOWED_CATEGORIES:
            self.logger.warning(
                f"Product {product.technical_id} has invalid category: '{product.category}'"
            )
            return False

        # Validate status
        if not product.status or product.status not in product.ALLOWED_STATUSES:
            self.logger.warning(
                f"Product {product.technical_id} has invalid status: '{product.status}'"
            )
            return False

        return True

    def _validate_data_ranges(self, product: Product) -> bool:
        """
        Validate data types and value ranges.

        Args:
            product: The Product entity to validate

        Returns:
            True if all data ranges are valid, False otherwise
        """
        # Validate price
        if product.price is not None:
            if product.price < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative price: {product.price}"
                )
                return False
            if product.price > 100000:  # Reasonable upper limit
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
            if product.sales_volume > 10000:  # Reasonable upper limit
                self.logger.warning(
                    f"Product {product.technical_id} has unrealistic sales volume: {product.sales_volume}"
                )
                return False

        # Validate stock level
        if product.stock_level is not None:
            if product.stock_level < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative stock level: {product.stock_level}"
                )
                return False

        # Validate reorder point
        if product.reorder_point is not None:
            if product.reorder_point < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative reorder point: {product.reorder_point}"
                )
                return False

        # Validate performance metrics if present
        if product.performance_score is not None:
            if product.performance_score < 0 or product.performance_score > 100:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid performance score: {product.performance_score}"
                )
                return False

        if product.inventory_turnover_rate is not None:
            if product.inventory_turnover_rate < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative turnover rate: {product.inventory_turnover_rate}"
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
        # Rule: Products with sales data should have price information
        if product.sales_volume is not None and product.sales_volume > 0:
            if product.price is None or product.price <= 0:
                self.logger.warning(
                    f"Product {product.technical_id} has sales but no valid price"
                )
                return False

        # Rule: Revenue should match price * sales_volume if both are present
        if (
            product.price is not None
            and product.sales_volume is not None
            and product.revenue is not None
        ):
            expected_revenue = product.price * product.sales_volume
            if (
                abs(product.revenue - expected_revenue) > 0.01
            ):  # Allow small floating point differences
                self.logger.warning(
                    f"Product {product.technical_id} revenue mismatch: "
                    f"expected {expected_revenue}, got {product.revenue}"
                )
                return False

        # Rule: Reorder point should be reasonable compared to stock level
        if product.stock_level is not None and product.reorder_point is not None:
            if product.reorder_point > product.stock_level * 2:
                self.logger.warning(
                    f"Product {product.technical_id} has unrealistic reorder point: "
                    f"{product.reorder_point} vs stock {product.stock_level}"
                )
                return False

        # Rule: Sold products should have sales volume
        if product.status == "sold":
            if product.sales_volume is None or product.sales_volume <= 0:
                self.logger.warning(
                    f"Product {product.technical_id} marked as sold but no sales volume"
                )
                return False

        return True

    def _validate_api_data(self, product: Product) -> bool:
        """
        Validate API data integrity and consistency.

        Args:
            product: The Product entity to validate

        Returns:
            True if API data is valid, False otherwise
        """
        # Validate API source
        if product.api_source and product.api_source not in [
            "petstore",
            "petstore_inventory",
            "petstore_pets",
        ]:
            self.logger.warning(
                f"Product {product.technical_id} has unknown API source: {product.api_source}"
            )
            return False

        # Validate API ID format if present
        if product.api_id is not None:
            if len(str(product.api_id)) == 0:
                self.logger.warning(f"Product {product.technical_id} has empty API ID")
                return False

        # Validate timestamp formats
        timestamp_fields = [
            product.created_at,
            product.updated_at,
            product.last_analyzed_at,
        ]
        for timestamp in timestamp_fields:
            if timestamp is not None:
                if not self._validate_timestamp_format(timestamp):
                    self.logger.warning(
                        f"Product {product.technical_id} has invalid timestamp format: {timestamp}"
                    )
                    return False

        return True

    def _validate_timestamp_format(self, timestamp: str) -> bool:
        """
        Validate ISO 8601 timestamp format.

        Args:
            timestamp: Timestamp string to validate

        Returns:
            True if format is valid, False otherwise
        """
        try:
            from datetime import datetime

            # Try to parse ISO format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            return False
