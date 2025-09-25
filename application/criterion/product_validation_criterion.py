"""
ProductValidationCriterion for Pet Store Performance Analysis System

Validates that a Product entity meets all required business rules before it can
proceed to data extraction stage as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.product import Product


class ProductValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Product entity that checks all business rules
    before the entity can proceed to data extraction stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductValidationCriterion",
            description="Validates Product business rules and data consistency",
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

            # Validate field formats and constraints
            if not self._validate_field_constraints(product):
                return False

            # Validate business logic rules
            if not self._validate_business_rules(product):
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
        Validate that all required fields are present and non-empty.

        Args:
            product: The Product entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate product name
        if not product.name or len(product.name.strip()) == 0:
            self.logger.warning(
                f"Product {product.technical_id} has empty or missing name"
            )
            return False

        if len(product.name.strip()) < 2:
            self.logger.warning(
                f"Product {product.technical_id} name too short: '{product.name}'"
            )
            return False

        if len(product.name) > 200:
            self.logger.warning(
                f"Product {product.technical_id} name too long: {len(product.name)} characters"
            )
            return False

        # Validate category
        if not product.category:
            self.logger.warning(
                f"Product {product.technical_id} has missing category"
            )
            return False

        if product.category not in product.ALLOWED_CATEGORIES:
            self.logger.warning(
                f"Product {product.technical_id} has invalid category: {product.category}"
            )
            return False

        return True

    def _validate_field_constraints(self, product: Product) -> bool:
        """
        Validate field constraints and data types.

        Args:
            product: The Product entity to validate

        Returns:
            True if all field constraints are met, False otherwise
        """
        # Validate numeric fields are non-negative
        if product.sales_volume is not None and product.sales_volume < 0:
            self.logger.warning(
                f"Product {product.technical_id} has negative sales volume: {product.sales_volume}"
            )
            return False

        if product.revenue is not None and product.revenue < 0:
            self.logger.warning(
                f"Product {product.technical_id} has negative revenue: {product.revenue}"
            )
            return False

        if product.inventory_level is not None and product.inventory_level < 0:
            self.logger.warning(
                f"Product {product.technical_id} has negative inventory level: {product.inventory_level}"
            )
            return False

        # Validate performance score range
        if product.performance_score is not None:
            if product.performance_score < 0 or product.performance_score > 100:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid performance score: {product.performance_score}"
                )
                return False

        # Validate stock status
        if product.stock_status and product.stock_status not in product.ALLOWED_STOCK_STATUS:
            self.logger.warning(
                f"Product {product.technical_id} has invalid stock status: {product.stock_status}"
            )
            return False

        return True

    def _validate_business_rules(self, product: Product) -> bool:
        """
        Validate business logic rules specific to the Pet Store domain.

        Args:
            product: The Product entity to validate

        Returns:
            True if all business rules are met, False otherwise
        """
        # Validate stock status consistency with inventory level
        if product.inventory_level is not None and product.stock_status:
            if product.inventory_level == 0 and product.stock_status not in ["OUT_OF_STOCK", "UNKNOWN"]:
                self.logger.warning(
                    f"Product {product.technical_id} has zero inventory but status is {product.stock_status}"
                )
                return False

            if product.inventory_level > 0 and product.stock_status == "OUT_OF_STOCK":
                self.logger.warning(
                    f"Product {product.technical_id} has inventory but status is OUT_OF_STOCK"
                )
                return False

        # Validate revenue consistency with sales volume
        if (product.sales_volume is not None and product.revenue is not None and 
            product.sales_volume > 0 and product.revenue == 0):
            self.logger.warning(
                f"Product {product.technical_id} has sales volume but zero revenue"
            )
            return False

        # Category-specific validation rules
        if not self._validate_category_specific_rules(product):
            return False

        return True

    def _validate_category_specific_rules(self, product: Product) -> bool:
        """
        Validate category-specific business rules.

        Args:
            product: The Product entity to validate

        Returns:
            True if category-specific rules are met, False otherwise
        """
        category = product.category

        # High-demand categories should have reasonable inventory levels
        high_demand_categories = ["FOOD", "TOYS", "DOGS", "CATS"]
        if (category in high_demand_categories and 
            product.inventory_level is not None and 
            product.inventory_level == 0 and 
            product.stock_status != "OUT_OF_STOCK"):
            self.logger.warning(
                f"High-demand product {product.technical_id} ({category}) has zero inventory"
            )
            # This is a warning, not a failure - allow processing to continue
            
        # Specialty categories might have lower inventory levels
        specialty_categories = ["REPTILES", "BIRDS"]
        if (category in specialty_categories and 
            product.inventory_level is not None and 
            product.inventory_level > 100):
            self.logger.info(
                f"Specialty product {product.technical_id} ({category}) has high inventory: {product.inventory_level}"
            )
            # This is just informational

        # Health products should have proper naming conventions
        if category == "HEALTH":
            health_keywords = ["vitamin", "supplement", "medicine", "treatment", "care", "health"]
            name_lower = product.name.lower()
            if not any(keyword in name_lower for keyword in health_keywords):
                self.logger.info(
                    f"Health product {product.technical_id} name might not indicate health purpose: {product.name}"
                )
                # This is informational, not a validation failure

        return True

    def _validate_data_consistency(self, product: Product) -> bool:
        """
        Validate data consistency across related fields.

        Args:
            product: The Product entity to validate

        Returns:
            True if data is consistent, False otherwise
        """
        # Check if performance score is consistent with other metrics
        if (product.performance_score is not None and 
            product.sales_volume is not None and 
            product.revenue is not None):
            
            # High performance score should correlate with good metrics
            if (product.performance_score >= 80 and 
                (product.sales_volume <= 10 or product.revenue <= 100)):
                self.logger.warning(
                    f"Product {product.technical_id} has high performance score ({product.performance_score}) "
                    f"but low sales/revenue (sales: {product.sales_volume}, revenue: {product.revenue})"
                )
                # This is a warning, not a validation failure

            # Low performance score should correlate with poor metrics
            if (product.performance_score <= 20 and 
                (product.sales_volume >= 100 or product.revenue >= 1000)):
                self.logger.warning(
                    f"Product {product.technical_id} has low performance score ({product.performance_score}) "
                    f"but high sales/revenue (sales: {product.sales_volume}, revenue: {product.revenue})"
                )
                # This is a warning, not a validation failure

        return True

    def _validate_temporal_consistency(self, product: Product) -> bool:
        """
        Validate temporal consistency of timestamps.

        Args:
            product: The Product entity to validate

        Returns:
            True if timestamps are consistent, False otherwise
        """
        # Validate that data_extracted_at is not in the future
        if product.data_extracted_at:
            try:
                from datetime import datetime, timezone
                extracted_time = datetime.fromisoformat(product.data_extracted_at.replace("Z", "+00:00"))
                current_time = datetime.now(timezone.utc)
                
                if extracted_time > current_time:
                    self.logger.warning(
                        f"Product {product.technical_id} has future data extraction timestamp: {product.data_extracted_at}"
                    )
                    return False
            except ValueError:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid data extraction timestamp format: {product.data_extracted_at}"
                )
                return False

        # Validate that analyzed_at is after data_extracted_at
        if product.data_extracted_at and product.analyzed_at:
            try:
                from datetime import datetime
                extracted_time = datetime.fromisoformat(product.data_extracted_at.replace("Z", "+00:00"))
                analyzed_time = datetime.fromisoformat(product.analyzed_at.replace("Z", "+00:00"))
                
                if analyzed_time < extracted_time:
                    self.logger.warning(
                        f"Product {product.technical_id} has analysis timestamp before extraction timestamp"
                    )
                    return False
            except ValueError:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid timestamp format"
                )
                return False

        return True
