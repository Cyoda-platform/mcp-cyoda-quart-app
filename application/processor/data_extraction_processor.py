"""
DataExtractionProcessor for Pet Store Performance Analysis System

Handles automated data extraction from Pet Store API including HTTP requests,
data transformation, and Product entity creation as specified in functional requirements.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class DataExtractionProcessor(CyodaProcessor):
    """
    Processor for DataExtraction entity that handles automated data collection
    from Pet Store API and creates Product entities for analysis.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionProcessor",
            description="Handles automated data extraction from Pet Store API and Product creation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Execute data extraction from Pet Store API and create Product entities.

        Args:
            entity: The DataExtraction entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed DataExtraction entity with results
        """
        try:
            self.logger.info(
                f"Starting data extraction: {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction = cast_entity(entity, DataExtraction)

            # Mark extraction as started
            extraction.mark_extraction_started()
            start_time = datetime.now(timezone.utc)

            # Extract data from Pet Store API
            extracted_data = await self._extract_from_api(extraction)

            if extracted_data:
                # Set extracted data and calculate quality score
                extraction.set_extracted_data(extracted_data)
                extraction.calculate_data_quality_score()

                # Create Product entities from extracted data
                await self._create_product_entities(extracted_data)

                # Mark extraction as completed
                end_time = datetime.now(timezone.utc)
                duration_ms = int((end_time - start_time).total_seconds() * 1000)
                extraction.mark_extraction_completed(len(extracted_data), duration_ms)

                self.logger.info(
                    f"Data extraction {extraction.technical_id} completed successfully - "
                    f"Extracted {len(extracted_data)} products in {duration_ms}ms"
                )
            else:
                extraction.mark_extraction_failed("No data retrieved from API")
                self.logger.error(
                    f"Data extraction {extraction.technical_id} failed - no data retrieved"
                )

            return extraction

        except Exception as e:
            self.logger.error(
                f"Error in data extraction {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            if hasattr(entity, "mark_extraction_failed"):
                entity.mark_extraction_failed(str(e))
            raise

    async def _extract_from_api(
        self, extraction: DataExtraction
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Extract data from Pet Store API.

        Args:
            extraction: The DataExtraction entity

        Returns:
            List of extracted product data or None if failed
        """
        try:
            # Simulate API call to Pet Store API
            # In real implementation, this would make actual HTTP requests
            self.logger.info(f"Extracting data from {extraction.api_endpoint}")

            # Simulate API response delay
            await asyncio.sleep(0.5)

            # Generate simulated pet store data
            simulated_data = self._generate_simulated_pet_store_data()

            self.logger.info(
                f"Successfully extracted {len(simulated_data)} products from API"
            )
            return simulated_data

        except Exception as e:
            self.logger.error(f"API extraction failed: {str(e)}")
            return None

    def _generate_simulated_pet_store_data(self) -> List[Dict[str, Any]]:
        """
        Generate simulated pet store data for demonstration.
        In real implementation, this would be replaced with actual API calls.

        Returns:
            List of simulated product data
        """
        import random

        categories = ["dog", "cat", "bird", "fish", "reptile", "small-pet"]
        statuses = ["available", "pending", "sold"]

        products = []

        # Generate 20 sample products
        for i in range(1, 21):
            category = random.choice(categories)
            status = random.choice(statuses)

            # Generate realistic sales and inventory data
            base_price = random.uniform(10.0, 200.0)
            sales_volume = random.randint(0, 150)
            inventory_level = random.randint(0, 200)

            product_data = {
                "id": f"pet-{i:03d}",
                "name": f"{category.title()} Product {i}",
                "category": category,
                "status": status,
                "price": round(base_price, 2),
                "sales_volume": sales_volume,
                "inventory_level": inventory_level,
                "photoUrls": [f"https://example.com/pet-{i}.jpg"],
                "tags": [{"id": i, "name": f"{category}-tag"}],
            }

            products.append(product_data)

        return products

    async def _create_product_entities(
        self, extracted_data: List[Dict[str, Any]]
    ) -> None:
        """
        Create Product entities from extracted data.

        Args:
            extracted_data: List of product data from API
        """
        entity_service = get_entity_service()
        created_count = 0

        for product_data in extracted_data:
            try:
                # Transform API data to Product entity format
                product = self._transform_to_product_entity(product_data)

                # Convert to dict for EntityService
                product_dict = product.model_dump(by_alias=True)

                # Save the Product entity
                response = await entity_service.save(
                    entity=product_dict,
                    entity_class=Product.ENTITY_NAME,
                    entity_version=str(Product.ENTITY_VERSION),
                )

                created_product_id = response.metadata.id
                created_count += 1

                self.logger.debug(
                    f"Created Product entity {created_product_id} for {product.product_id}"
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to create Product entity for {product_data.get('id', 'unknown')}: {str(e)}"
                )
                continue

        self.logger.info(
            f"Successfully created {created_count} Product entities from extracted data"
        )

    def _transform_to_product_entity(self, api_data: Dict[str, Any]) -> Product:
        """
        Transform API data to Product entity format.

        Args:
            api_data: Raw data from Pet Store API

        Returns:
            Product entity instance
        """
        # Extract and transform fields from API response
        product_id = str(api_data.get("id", ""))
        name = api_data.get("name", "Unknown Product")
        category = api_data.get("category", "unknown")
        status = api_data.get("status", "available")

        # Handle price data
        price = api_data.get("price")
        if price is None:
            # Generate price based on category if not provided
            category_prices = {
                "dog": 50.0,
                "cat": 40.0,
                "bird": 30.0,
                "fish": 25.0,
                "reptile": 60.0,
                "small-pet": 35.0,
            }
            price = category_prices.get(category, 40.0)

        # Extract sales and inventory data
        sales_volume = api_data.get("sales_volume", 0)
        inventory_level = api_data.get("inventory_level", 0)

        # Calculate revenue
        revenue = sales_volume * price if sales_volume and price else 0.0

        # Create Product entity
        product = Product(
            product_id=product_id,
            name=name,
            category=category,
            status=status,
            price=price,
            sales_volume=sales_volume,
            revenue=revenue,
            inventory_level=inventory_level,
        )

        # Set extraction timestamp
        product.update_extraction_timestamp()

        return product
