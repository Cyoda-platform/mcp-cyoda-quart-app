"""
ProductValidationCriterion for Pet Store Performance Analysis System

Validates that a Product entity meets all required business rules before
it can proceed to the analysis stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.product.version_1.product import Product


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
            if not product.name or len(product.name.strip()) < 1:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid name: '{product.name}'"
                )
                return False

            if not product.category:
                self.logger.warning(
                    f"Product {product.technical_id} missing category"
                )
                return False

            if not product.status:
                self.logger.warning(
                    f"Product {product.technical_id} missing status"
                )
                return False

            # Validate category is in allowed list
            if product.category not in Product.ALLOWED_CATEGORIES:
                self.logger.warning(
                    f"Product {product.technical_id} has invalid category: {product.category}"
                )
                return False

            # Validate status is in allowed list
            if product.status not in Product.ALLOWED_STATUSES:
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

            if product.inventory_level is not None and product.inventory_level < 0:
                self.logger.warning(
                    f"Product {product.technical_id} has negative inventory: {product.inventory_level}"
                )
                return False

            # Business logic validation
            # Products with "sold" status should have sales volume > 0
            if product.status == "sold" and (product.sales_volume is None or product.sales_volume == 0):
                self.logger.warning(
                    f"Product {product.technical_id} marked as sold but has no sales volume"
                )
                return False

            # Products with revenue should have sales volume
            if (product.revenue is not None and product.revenue > 0 and 
                (product.sales_volume is None or product.sales_volume == 0)):
                self.logger.warning(
                    f"Product {product.technical_id} has revenue but no sales volume"
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
