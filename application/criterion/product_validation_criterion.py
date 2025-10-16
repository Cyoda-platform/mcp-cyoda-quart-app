"""
ProductValidationCriterion for Cyoda OMS Application

Validates that a Product meets all required business rules before it can
proceed to the active stage as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.product.version_1.product import Product


class ProductValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Product that checks all business rules
    before the product can proceed to active stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductValidationCriterion",
            description="Validates Product business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the product meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Product)
            **kwargs: Additional criteria parameters

        Returns:
            True if the product meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating product {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Validate required fields
            if not product.sku or len(product.sku.strip()) == 0:
                self.logger.warning(f"Product {product.technical_id} has invalid SKU")
                return False

            if not product.name or len(product.name.strip()) == 0:
                self.logger.warning(f"Product {product.technical_id} has invalid name")
                return False

            if not product.description or len(product.description.strip()) == 0:
                self.logger.warning(f"Product {product.technical_id} has invalid description")
                return False

            if product.price < 0:
                self.logger.warning(f"Product {product.technical_id} has negative price: {product.price}")
                return False

            if product.quantityAvailable < 0:
                self.logger.warning(f"Product {product.technical_id} has negative quantity: {product.quantityAvailable}")
                return False

            if not product.category or len(product.category.strip()) == 0:
                self.logger.warning(f"Product {product.technical_id} has invalid category")
                return False

            self.logger.info(f"Product {product.technical_id} passed all validation criteria")
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
