"""
ProductValidationCriterion for Pet Store Performance Analysis System

Validates that a Product entity meets all required business rules before it can
proceed to analysis stage as specified in functional requirements.
"""

from typing import Any

from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ProductValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Product entity that checks all business rules
    before the entity can proceed to analysis stage.
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
            if not product.name or len(product.name.strip()) < 3:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid name: '{product.name}'"
                )
                return False

            if (
                not product.category
                or product.category not in Product.ALLOWED_CATEGORIES
            ):
                self.logger.warning(
                    f"Product {product.technical_id} has invalid category: {product.category}"
                )
                return False

            if not product.status or product.status not in Product.ALLOWED_STATUSES:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid status: {product.status}"
                )
                return False

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

            if product.stock_level is not None and product.stock_level < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative stock level: {product.stock_level}"
                )
                return False

            # Business logic validation
            if product.status == "sold" and (product.stock_level or 0) > 0:
                self.logger.warning(
                    f"Product {product.technical_id} marked as sold but has stock: {product.stock_level}"
                )
                return False

            self.logger.info(
                f"Product {product.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating Product entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
