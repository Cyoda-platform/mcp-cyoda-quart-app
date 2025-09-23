"""
ProductDataValidationCriterion for Product Performance Analysis System

Validates ProductData entities for data quality and business rules
before processing as specified in functional requirements.
"""

from typing import Any

from application.entity.product_data.version_1.product_data import ProductData
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ProductDataValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for ProductData entities.

    Checks data quality, required fields, and business rules before
    allowing ProductData entities to proceed to data extraction.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductDataValidationCriterion",
            description="Validates ProductData entities for data quality and business rules",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the ProductData entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be ProductData)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating ProductData entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to ProductData for type-safe operations
            product_data = cast_entity(entity, ProductData)

            # Validate required fields
            if not self._validate_required_fields(product_data):
                return False

            # Validate field formats and constraints
            if not self._validate_field_constraints(product_data):
                return False

            # Validate business rules
            if not self._validate_business_rules(product_data):
                return False

            self.logger.info(
                f"ProductData entity {product_data.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, product_data: ProductData) -> bool:
        """
        Validate that all required fields are present and non-empty.

        Args:
            product_data: The ProductData entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate product_id
        if not product_data.product_id or len(product_data.product_id.strip()) == 0:
            self.logger.warning(
                f"Entity {product_data.technical_id} has invalid product_id: '{product_data.product_id}'"
            )
            return False

        # Validate name (if provided)
        if product_data.name and len(product_data.name.strip()) == 0:
            self.logger.warning(
                f"Entity {product_data.technical_id} has empty name field"
            )
            return False

        # Validate category (if provided)
        if product_data.category and len(product_data.category.strip()) == 0:
            self.logger.warning(
                f"Entity {product_data.technical_id} has empty category field"
            )
            return False

        # Validate status (if provided)
        if product_data.status and product_data.status not in [
            "available",
            "pending",
            "sold",
        ]:
            self.logger.warning(
                f"Entity {product_data.technical_id} has invalid status: '{product_data.status}'"
            )
            return False

        return True

    def _validate_field_constraints(self, product_data: ProductData) -> bool:
        """
        Validate field constraints and formats.

        Args:
            product_data: The ProductData entity to validate

        Returns:
            True if all field constraints are met, False otherwise
        """
        # Validate numeric fields are non-negative
        if product_data.sales_volume is not None and product_data.sales_volume < 0:
            self.logger.warning(
                f"Entity {product_data.technical_id} has negative sales_volume: {product_data.sales_volume}"
            )
            return False

        if product_data.revenue is not None and product_data.revenue < 0:
            self.logger.warning(
                f"Entity {product_data.technical_id} has negative revenue: {product_data.revenue}"
            )
            return False

        if product_data.stock_level is not None and product_data.stock_level < 0:
            self.logger.warning(
                f"Entity {product_data.technical_id} has negative stock_level: {product_data.stock_level}"
            )
            return False

        if (
            product_data.inventory_turnover_rate is not None
            and product_data.inventory_turnover_rate < 0
        ):
            self.logger.warning(
                f"Entity {product_data.technical_id} has negative inventory_turnover_rate: {product_data.inventory_turnover_rate}"
            )
            return False

        if product_data.performance_score is not None and (
            product_data.performance_score < 0 or product_data.performance_score > 100
        ):
            self.logger.warning(
                f"Entity {product_data.technical_id} has invalid performance_score: {product_data.performance_score} (must be 0-100)"
            )
            return False

        # Validate data format
        if product_data.data_format and product_data.data_format not in ["json", "xml"]:
            self.logger.warning(
                f"Entity {product_data.technical_id} has invalid data_format: '{product_data.data_format}'"
            )
            return False

        return True

    def _validate_business_rules(self, product_data: ProductData) -> bool:
        """
        Validate business rules and logical constraints.

        Args:
            product_data: The ProductData entity to validate

        Returns:
            True if all business rules are satisfied, False otherwise
        """
        # Business rule: If sales_volume and stock_level are both provided,
        # inventory turnover should be reasonable
        if (
            product_data.sales_volume is not None
            and product_data.stock_level is not None
            and product_data.inventory_turnover_rate is not None
        ):

            if product_data.stock_level > 0:
                expected_turnover = product_data.sales_volume / product_data.stock_level
                actual_turnover = product_data.inventory_turnover_rate

                # Allow for some variance in calculation
                if abs(expected_turnover - actual_turnover) > 0.1:
                    self.logger.warning(
                        f"Entity {product_data.technical_id} has inconsistent inventory turnover calculation: "
                        f"expected {expected_turnover:.2f}, actual {actual_turnover:.2f}"
                    )
                    # This is a warning, not a failure - data might be from different time periods

        # Business rule: High performance score should correlate with high sales or revenue
        if (
            product_data.performance_score is not None
            and product_data.performance_score > 80
            and product_data.sales_volume is not None
            and product_data.revenue is not None
        ):

            if product_data.sales_volume == 0 and product_data.revenue == 0:
                self.logger.warning(
                    f"Entity {product_data.technical_id} has high performance score ({product_data.performance_score}) "
                    f"but zero sales and revenue"
                )
                return False

        # Business rule: Sold items should not require restocking
        if product_data.status == "sold" and product_data.requires_restocking is True:
            self.logger.warning(
                f"Entity {product_data.technical_id} is marked as 'sold' but requires restocking"
            )
            # This might be valid if it's a popular item that sold out

        # Business rule: API source should be consistent with data format
        if (
            product_data.api_source
            and product_data.data_format
            and product_data.api_source == "petstore"
            and product_data.data_format not in ["json", "xml"]
        ):
            self.logger.warning(
                f"Entity {product_data.technical_id} has inconsistent API source and data format"
            )
            return False

        return True
