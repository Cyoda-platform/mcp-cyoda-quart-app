"""
DataExtractionProcessor for Pet Store Performance Analysis System

Handles automated data extraction from Pet Store API as specified in the
functional requirements for scheduled data collection every Monday.
"""

import json
import logging
from typing import Any, Dict, List, Optional
import asyncio
import aiohttp

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from application.entity.product.version_1.product import Product
from services.services import get_entity_service


class DataExtractionProcessor(CyodaProcessor):
    """
    Processor for DataExtraction entity that handles automated data collection
    from Pet Store API and creates Product entities for analysis.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionProcessor",
            description="Extracts data from Pet Store API and creates Product entities",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the DataExtraction entity to fetch data from Pet Store API.

        Args:
            entity: The DataExtraction entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with extraction results
        """
        try:
            self.logger.info(
                f"Starting data extraction {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction = cast_entity(entity, DataExtraction)

            # Mark extraction as started
            extraction.mark_execution_start()

            # Extract data from Pet Store API
            extracted_data = await self._extract_from_api(extraction)

            if extracted_data:
                extraction.extracted_data = extracted_data

                # Process the extracted data and create Product entities
                products_created = await self._process_extracted_data(
                    extraction, extracted_data
                )

                # Mark extraction as completed
                extraction.mark_execution_complete(products_created)

                # Schedule next execution
                extraction.schedule_next_execution()

                self.logger.info(
                    f"Data extraction {extraction.technical_id} completed successfully. "
                    f"Created {products_created} products."
                )
            else:
                extraction.mark_execution_failed("No data extracted from API")
                self.logger.error(
                    f"Data extraction {extraction.technical_id} failed - no data received"
                )

            return extraction

        except Exception as e:
            self.logger.error(
                f"Error in data extraction {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark extraction as failed
            if isinstance(entity, DataExtraction):
                entity.mark_execution_failed(str(e))
            raise

    async def _extract_from_api(
        self, extraction: DataExtraction
    ) -> Optional[Dict[str, Any]]:
        """
        Extract data from Pet Store API.

        Args:
            extraction: The DataExtraction entity with API configuration

        Returns:
            Extracted data dictionary or None if failed
        """
        try:
            timeout = aiohttp.ClientTimeout(total=extraction.timeout_seconds)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Get available pets from Pet Store API
                pets_url = f"{extraction.api_endpoint}/pet/findByStatus"
                params = {"status": "available"}

                self.logger.info(f"Fetching data from {pets_url}")

                async with session.get(pets_url, params=params) as response:
                    if response.status == 200:
                        if extraction.data_format == "json":
                            data = await response.json()
                        else:
                            # Handle XML format if needed
                            text_data = await response.text()
                            data = {"raw_xml": text_data}

                        self.logger.info(
                            f"Successfully extracted data: {len(data) if isinstance(data, list) else 1} items"
                        )
                        return {
                            "pets": data,
                            "extraction_timestamp": extraction.last_execution,
                        }
                    else:
                        error_msg = f"API request failed with status {response.status}"
                        extraction.add_extraction_error(error_msg)
                        self.logger.error(error_msg)
                        return None

        except asyncio.TimeoutError:
            error_msg = (
                f"API request timed out after {extraction.timeout_seconds} seconds"
            )
            extraction.add_extraction_error(error_msg)
            self.logger.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"API extraction failed: {str(e)}"
            extraction.add_extraction_error(error_msg)
            self.logger.error(error_msg)
            return None

    async def _process_extracted_data(
        self, extraction: DataExtraction, data: Dict[str, Any]
    ) -> int:
        """
        Process extracted data and create Product entities.

        Args:
            extraction: The DataExtraction entity
            data: Extracted data from API

        Returns:
            Number of products successfully created
        """
        entity_service = get_entity_service()
        products_created = 0
        products_failed = 0

        pets_data = data.get("pets", [])
        if not isinstance(pets_data, list):
            self.logger.warning("Extracted data is not a list, cannot process pets")
            return 0

        for pet_data in pets_data:
            try:
                # Create Product entity from pet data
                product = self._create_product_from_pet(pet_data)

                if product:
                    # Save the product using entity service
                    product_data = product.model_dump(by_alias=True)

                    response = await entity_service.save(
                        entity=product_data,
                        entity_class=Product.ENTITY_NAME,
                        entity_version=str(Product.ENTITY_VERSION),
                    )

                    products_created += 1
                    self.logger.debug(f"Created product: {response.metadata.id}")
                else:
                    products_failed += 1

            except Exception as e:
                products_failed += 1
                error_msg = f"Failed to create product from pet data: {str(e)}"
                extraction.add_extraction_error(error_msg)
                self.logger.warning(error_msg)
                continue

        # Update extraction statistics
        extraction.processed_products = products_created
        extraction.failed_products = products_failed

        self.logger.info(
            f"Processed {len(pets_data)} pets: {products_created} products created, {products_failed} failed"
        )

        return products_created

    def _create_product_from_pet(self, pet_data: Dict[str, Any]) -> Optional[Product]:
        """
        Create a Product entity from Pet Store API pet data.

        Args:
            pet_data: Pet data from API

        Returns:
            Product entity or None if creation failed
        """
        try:
            # Extract basic information
            name = pet_data.get("name", "Unknown Pet")
            pet_id = pet_data.get("id")
            status = pet_data.get("status", "available")

            # Determine category from tags or default
            category = self._determine_category(pet_data)

            # Generate simulated performance data
            sales_data = self._generate_sales_data(pet_data)

            # Create Product entity
            product = Product(
                name=name,
                category=category,
                status=status,
                pet_store_id=pet_id,
                sales_volume=sales_data["sales_volume"],
                revenue=sales_data["revenue"],
                inventory_level=sales_data["inventory_level"],
                tags=self._extract_tags(pet_data),
            )

            return product

        except Exception as e:
            self.logger.error(f"Error creating product from pet data: {str(e)}")
            return None

    def _determine_category(self, pet_data: Dict[str, Any]) -> str:
        """
        Determine product category from pet data.

        Args:
            pet_data: Pet data from API

        Returns:
            Product category string
        """
        # Check if category is in tags
        tags = pet_data.get("tags", [])
        if tags:
            for tag in tags:
                tag_name = tag.get("name", "").lower()
                if tag_name in Product.ALLOWED_CATEGORIES:
                    return tag_name

        # Check pet name for category hints
        name = pet_data.get("name", "").lower()
        if any(word in name for word in ["dog", "puppy", "canine"]):
            return "dog"
        elif any(word in name for word in ["cat", "kitten", "feline"]):
            return "cat"
        elif any(word in name for word in ["bird", "parrot", "canary"]):
            return "bird"
        elif any(word in name for word in ["fish", "goldfish", "aquarium"]):
            return "fish"
        elif any(word in name for word in ["reptile", "snake", "lizard", "turtle"]):
            return "reptile"
        else:
            return "small-pet"  # Default category

    def _generate_sales_data(self, pet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate simulated sales data for the product.

        Args:
            pet_data: Pet data from API

        Returns:
            Dictionary with sales volume, revenue, and inventory data
        """
        import random

        # Use pet ID as seed for consistent data generation
        pet_id = pet_data.get("id", 1)
        random.seed(pet_id)

        # Generate realistic sales data
        sales_volume = random.randint(0, 150)
        unit_price = random.uniform(10.0, 500.0)
        revenue = sales_volume * unit_price
        inventory_level = random.randint(0, 200)

        return {
            "sales_volume": sales_volume,
            "revenue": round(revenue, 2),
            "inventory_level": inventory_level,
        }

    def _extract_tags(self, pet_data: Dict[str, Any]) -> List[str]:
        """
        Extract tags from pet data.

        Args:
            pet_data: Pet data from API

        Returns:
            List of tag strings
        """
        tags = []
        pet_tags = pet_data.get("tags", [])

        for tag in pet_tags:
            if isinstance(tag, dict) and "name" in tag:
                tags.append(tag["name"])
            elif isinstance(tag, str):
                tags.append(tag)

        return tags
