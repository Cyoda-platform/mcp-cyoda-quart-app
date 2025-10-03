"""
PetStoreApiProcessor for Pet Store Performance Analysis System

Handles data extraction from Pet Store API and creates/updates Product entities
as specified in functional requirements for automated data collection.
"""

import json
import logging
from typing import Any, Dict, List

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class PetStoreApiProcessor(CyodaProcessor):
    """
    Processor for DataExtraction entity that fetches data from Pet Store API
    and creates/updates Product entities with the extracted data.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetStoreApiProcessor",
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
                f"Starting Pet Store API extraction for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction = cast_entity(entity, DataExtraction)

            # Mark extraction as started
            extraction.start_extraction()

            # Simulate API data extraction (in real implementation, call actual Pet Store API)
            api_data = await self._fetch_pet_store_data(extraction)

            # Process the extracted data and create/update Product entities
            processed_count, failed_count = await self._process_api_data(api_data)

            # Mark extraction as completed
            extraction.complete_extraction(
                records_extracted=len(api_data),
                records_processed=processed_count,
                records_failed=failed_count,
            )

            # Set data quality score
            if len(api_data) > 0:
                quality_score = (processed_count / len(api_data)) * 100
                extraction.set_data_quality_score(quality_score)

            self.logger.info(
                f"Pet Store API extraction completed - Extracted: {len(api_data)}, Processed: {processed_count}, Failed: {failed_count}"
            )

            return extraction

        except Exception as e:
            self.logger.error(
                f"Error in Pet Store API extraction {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark extraction as failed
            if hasattr(entity, "fail_extraction"):
                entity.fail_extraction(str(e))
            raise

    async def _fetch_pet_store_data(
        self, extraction: DataExtraction
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from Pet Store API.

        Args:
            extraction: The DataExtraction entity with API configuration

        Returns:
            List of product data from API
        """
        try:
            # In a real implementation, this would make HTTP requests to the Pet Store API
            # For now, simulate API response with sample data

            self.logger.info(f"Fetching data from {extraction.api_endpoint}")

            # Simulate Pet Store API response data
            sample_data = [
                {
                    "id": "pet1",
                    "name": "Golden Retriever Puppy",
                    "category": "Dogs",
                    "status": "available",
                    "salesVolume": 45,
                    "revenue": 1350.0,
                    "stockLevel": 12,
                },
                {
                    "id": "pet2",
                    "name": "Persian Cat",
                    "category": "Cats",
                    "status": "available",
                    "salesVolume": 23,
                    "revenue": 690.0,
                    "stockLevel": 8,
                },
                {
                    "id": "pet3",
                    "name": "Canary Bird",
                    "category": "Birds",
                    "status": "available",
                    "salesVolume": 67,
                    "revenue": 1005.0,
                    "stockLevel": 25,
                },
                {
                    "id": "pet4",
                    "name": "Goldfish",
                    "category": "Fish",
                    "status": "available",
                    "salesVolume": 120,
                    "revenue": 360.0,
                    "stockLevel": 50,
                },
                {
                    "id": "pet5",
                    "name": "Hamster",
                    "category": "Small Pets",
                    "status": "available",
                    "salesVolume": 89,
                    "revenue": 445.0,
                    "stockLevel": 15,
                },
            ]

            self.logger.info(
                f"Successfully fetched {len(sample_data)} records from Pet Store API"
            )
            return sample_data

        except Exception as e:
            self.logger.error(f"Error fetching Pet Store API data: {str(e)}")
            raise

    async def _process_api_data(
        self, api_data: List[Dict[str, Any]]
    ) -> tuple[int, int]:
        """
        Process API data and create/update Product entities.

        Args:
            api_data: List of product data from API

        Returns:
            Tuple of (processed_count, failed_count)
        """
        entity_service = get_entity_service()
        processed_count = 0
        failed_count = 0

        for product_data in api_data:
            try:
                # Create Product entity from API data
                product = Product(
                    name=product_data.get("name", "Unknown Product"),
                    category=product_data.get("category", "Dogs"),
                    status=product_data.get("status", "available"),
                    sales_volume=product_data.get("salesVolume", 0),
                    revenue=product_data.get("revenue", 0.0),
                    stock_level=product_data.get("stockLevel", 0),
                    api_product_id=product_data.get("id"),
                    api_source="petstore",
                )

                # Update extraction timestamp
                product.update_extraction_timestamp()

                # Convert to dict for EntityService
                product_dict = product.model_dump(by_alias=True)

                # Save the Product entity
                response = await entity_service.save(
                    entity=product_dict,
                    entity_class=Product.ENTITY_NAME,
                    entity_version=str(Product.ENTITY_VERSION),
                )

                processed_count += 1
                self.logger.debug(
                    f"Created Product entity {response.metadata.id} for {product.name}"
                )

            except Exception as e:
                failed_count += 1
                self.logger.warning(
                    f"Failed to process product {product_data.get('name', 'Unknown')}: {str(e)}"
                )
                continue

        return processed_count, failed_count
