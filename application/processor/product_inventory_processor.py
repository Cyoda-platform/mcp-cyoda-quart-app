"""
ProductInventoryProcessor for Cyoda OMS Application

Handles product inventory updates and validation
as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.product.version_1.product import Product


class ProductInventoryProcessor(CyodaProcessor):
    """
    Processor for Product that handles inventory updates and validation.
    Ensures inventory data consistency and updates timestamps.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductInventoryProcessor",
            description="Processes Product inventory updates and validation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Product inventory update.

        Args:
            entity: The Product entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed product with updated inventory
        """
        try:
            self.logger.info(
                f"Processing Product inventory update {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Update timestamp for inventory change
            product.update_timestamp()

            # Log inventory update
            self.logger.info(
                f"Product {product.sku} inventory updated: {product.quantityAvailable} units available"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error processing product inventory for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
