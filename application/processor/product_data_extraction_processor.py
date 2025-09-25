"""
ProductDataExtractionProcessor for Pet Store Performance Analysis System

Handles data extraction from the Pet Store API (https://petstore.swagger.io/#/)
and populates Product entities with sales and inventory data.
"""

import logging
import random
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ProductDataExtractionProcessor(CyodaProcessor):
    """
    Processor for Product entity that extracts data from Pet Store API
    and populates product performance metrics.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductDataExtractionProcessor",
            description="Extracts product data from Pet Store API and populates performance metrics",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Extract data from Pet Store API for the Product entity.

        Args:
            entity: The Product entity to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The product entity with extracted data
        """
        try:
            self.logger.info(
                f"Extracting data for Product {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Product for type-safe operations
            product = cast_entity(entity, Product)

            # Extract data from Pet Store API (simulated for this implementation)
            extracted_data = await self._extract_pet_store_data(product)

            # Update product with extracted data
            product.sales_volume = extracted_data["sales_volume"]
            product.revenue = extracted_data["revenue"]
            product.inventory_level = extracted_data["inventory_level"]
            product.pet_store_id = extracted_data["pet_store_id"]

            # Calculate and set stock status
            product.stock_status = product.calculate_stock_status()

            # Mark data as extracted
            product.set_data_extracted()

            self.logger.info(
                f"Product {product.technical_id} data extraction completed successfully"
            )

            return product

        except Exception as e:
            self.logger.error(
                f"Error extracting data for product {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _extract_pet_store_data(self, product: Product) -> Dict[str, Any]:
        """
        Extract data from Pet Store API for the given product.

        Note: This is a simulated implementation. In a real system, this would
        make actual HTTP requests to https://petstore.swagger.io/#/ API.

        Args:
            product: The Product entity to extract data for

        Returns:
            Dictionary containing extracted data
        """
        self.logger.info(
            f"Simulating Pet Store API data extraction for product: {product.name}"
        )

        # Simulate API call delay
        import asyncio

        await asyncio.sleep(0.1)

        # Generate realistic simulated data based on product category
        category_multipliers = {
            "DOGS": {"sales": 1.5, "revenue": 1.4, "inventory": 1.2},
            "CATS": {"sales": 1.3, "revenue": 1.3, "inventory": 1.1},
            "FISH": {"sales": 0.8, "revenue": 0.7, "inventory": 1.5},
            "BIRDS": {"sales": 0.6, "revenue": 0.8, "inventory": 1.3},
            "FOOD": {"sales": 2.0, "revenue": 1.8, "inventory": 0.8},
            "TOYS": {"sales": 1.2, "revenue": 1.0, "inventory": 1.4},
            "ACCESSORIES": {"sales": 1.0, "revenue": 1.1, "inventory": 1.2},
            "HEALTH": {"sales": 0.9, "revenue": 1.6, "inventory": 1.1},
            "REPTILES": {"sales": 0.4, "revenue": 0.6, "inventory": 1.6},
            "SMALL_PETS": {"sales": 0.7, "revenue": 0.9, "inventory": 1.3},
        }

        multiplier = category_multipliers.get(
            product.category, {"sales": 1.0, "revenue": 1.0, "inventory": 1.0}
        )

        # Generate base values with some randomness
        base_sales = random.randint(10, 500)
        base_price = random.uniform(5.0, 150.0)
        base_inventory = random.randint(0, 100)

        # Apply category-specific multipliers
        sales_volume = int(base_sales * multiplier["sales"])
        revenue = round(sales_volume * base_price * multiplier["revenue"], 2)
        inventory_level = int(base_inventory * multiplier["inventory"])

        # Generate a simulated Pet Store API ID
        pet_store_id = f"PS-{product.category[:3]}-{random.randint(1000, 9999)}"

        extracted_data = {
            "sales_volume": sales_volume,
            "revenue": revenue,
            "inventory_level": inventory_level,
            "pet_store_id": pet_store_id,
            "extraction_timestamp": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }

        self.logger.info(
            f"Extracted data for {product.name}: "
            f"Sales={sales_volume}, Revenue=${revenue:.2f}, Inventory={inventory_level}"
        )

        return extracted_data

    def _validate_api_response(self, response_data: Dict[str, Any]) -> bool:
        """
        Validate the response data from Pet Store API.

        Args:
            response_data: The response data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["sales_volume", "revenue", "inventory_level"]

        for field in required_fields:
            if field not in response_data:
                self.logger.warning(f"Missing required field in API response: {field}")
                return False

            if response_data[field] is None:
                self.logger.warning(f"Null value for required field: {field}")
                return False

        # Validate data types and ranges
        if (
            not isinstance(response_data["sales_volume"], int)
            or response_data["sales_volume"] < 0
        ):
            self.logger.warning("Invalid sales_volume in API response")
            return False

        if (
            not isinstance(response_data["revenue"], (int, float))
            or response_data["revenue"] < 0
        ):
            self.logger.warning("Invalid revenue in API response")
            return False

        if (
            not isinstance(response_data["inventory_level"], int)
            or response_data["inventory_level"] < 0
        ):
            self.logger.warning("Invalid inventory_level in API response")
            return False

        return True
