"""
DataExtractionProcessor for Pet Store Performance Analysis System

Handles data extraction from the Pet Store API, fetching product information
and creating Product entities for analysis as specified in functional requirements.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class DataExtractionProcessor(CyodaProcessor):
    """
    Processor for DataExtraction entities that fetches data from the Pet Store API
    and creates Product entities for performance analysis.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionProcessor",
            description="Extracts product data from Pet Store API and creates Product entities",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the DataExtraction entity to fetch data from Pet Store API.

        Args:
            entity: The DataExtraction entity to process (must be in 'scheduled' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed data extraction with results
        """
        try:
            self.logger.info(
                f"Starting data extraction {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction_job = cast_entity(entity, DataExtraction)

            # Start execution
            extraction_job.start_execution()

            # Perform data extraction
            success = await self._extract_data_from_api(extraction_job)

            if success:
                # Create Product entities if configured to do so
                if extraction_job.should_create_products():
                    await self._create_product_entities(extraction_job)

                extraction_job.complete_execution()
                self.logger.info(
                    f"Data extraction {extraction_job.technical_id} completed successfully - "
                    f"Extracted {extraction_job.total_records_extracted} records"
                )
            else:
                extraction_job.fail_execution("Data extraction failed")
                self.logger.error(
                    f"Data extraction {extraction_job.technical_id} failed"
                )

            return extraction_job

        except Exception as e:
            self.logger.error(
                f"Error processing DataExtraction {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            if hasattr(entity, "fail_execution"):
                entity.fail_execution(str(e))
            raise

    async def _extract_data_from_api(self, extraction_job: DataExtraction) -> bool:
        """
        Extract data from the Pet Store API.

        Args:
            extraction_job: The DataExtraction entity

        Returns:
            True if extraction was successful, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for endpoint in extraction_job.api_endpoints:
                    try:
                        url = f"{extraction_job.api_base_url}{endpoint}"
                        self.logger.info(f"Fetching data from: {url}")

                        # Prepare headers
                        headers = {"Accept": "application/json"}
                        if extraction_job.api_key:
                            headers["api_key"] = extraction_job.api_key

                        # Make API request
                        response = await client.get(url, headers=headers)

                        if response.status_code == 200:
                            data = response.json()

                            # Process the response data
                            if isinstance(data, list):
                                # Array of pets
                                for pet_data in data:
                                    self._process_pet_data(extraction_job, pet_data)
                            elif isinstance(data, dict):
                                # Single pet or error response
                                if "id" in data:  # Looks like a pet object
                                    self._process_pet_data(extraction_job, data)
                                else:
                                    self.logger.warning(
                                        f"Unexpected response format from {url}: {data}"
                                    )

                            extraction_job.record_successful_extraction()
                            self.logger.info(
                                f"Successfully extracted data from {endpoint}"
                            )

                        else:
                            error_msg = f"API request failed with status {response.status_code}: {response.text}"
                            self.logger.error(error_msg)
                            extraction_job.record_failed_extraction(error_msg)

                    except httpx.RequestError as e:
                        error_msg = f"Request error for {endpoint}: {str(e)}"
                        self.logger.error(error_msg)
                        extraction_job.record_failed_extraction(error_msg)

                    except Exception as e:
                        error_msg = f"Unexpected error for {endpoint}: {str(e)}"
                        self.logger.error(error_msg)
                        extraction_job.record_failed_extraction(error_msg)

                    # Small delay between requests to be respectful to the API
                    await asyncio.sleep(0.5)

            # Consider extraction successful if we got at least some data
            success_rate = extraction_job.get_success_rate()
            return success_rate > 0 and extraction_job.total_records_extracted > 0

        except Exception as e:
            error_msg = f"Critical error during data extraction: {str(e)}"
            self.logger.error(error_msg)
            extraction_job.record_failed_extraction(error_msg)
            return False

    def _process_pet_data(
        self, extraction_job: DataExtraction, pet_data: Dict[str, Any]
    ) -> None:
        """
        Process a single pet record from the API.

        Args:
            extraction_job: The DataExtraction entity
            pet_data: Raw pet data from the API
        """
        try:
            # Extract relevant fields from pet data
            processed_data = {
                "pet_id": pet_data.get("id"),
                "name": pet_data.get("name", "Unknown"),
                "status": pet_data.get("status", "available"),
                "photo_urls": pet_data.get("photoUrls", []),
                "tags": [],
            }

            # Process category information
            category = pet_data.get("category")
            if category:
                processed_data["category_id"] = category.get("id")
                processed_data["category_name"] = category.get("name")

            # Process tags
            tags = pet_data.get("tags", [])
            if tags:
                processed_data["tags"] = [
                    tag.get("name", "") for tag in tags if tag.get("name")
                ]

            # Add extraction metadata
            processed_data["extracted_at"] = extraction_job.started_at

            # Add to extracted data
            extraction_job.add_extracted_record(processed_data)

            self.logger.debug(
                f"Processed pet: {processed_data['name']} (ID: {processed_data['pet_id']})"
            )

        except Exception as e:
            self.logger.error(f"Error processing pet data: {str(e)}")
            # Don't fail the entire extraction for one bad record

    async def _create_product_entities(self, extraction_job: DataExtraction) -> None:
        """
        Create Product entities from extracted data.

        Args:
            extraction_job: The DataExtraction entity with extracted data
        """
        if not extraction_job.extracted_data:
            self.logger.warning("No extracted data to create Product entities from")
            return

        entity_service = get_entity_service()
        created_count = 0
        updated_count = 0

        for record in extraction_job.extracted_data:
            try:
                # Check if product already exists by pet_id
                existing_product = None
                if record.get("pet_id") and extraction_job.update_existing:
                    existing_product = await self._find_existing_product(
                        record["pet_id"]
                    )

                if existing_product:
                    # Update existing product
                    updated_product = await self._update_existing_product(
                        existing_product, record
                    )
                    if updated_product:
                        updated_count += 1
                        self.logger.debug(f"Updated existing product: {record['name']}")
                else:
                    # Create new product
                    new_product = await self._create_new_product(record)
                    if new_product:
                        created_count += 1
                        self.logger.debug(f"Created new product: {record['name']}")

            except Exception as e:
                self.logger.error(
                    f"Error creating/updating product for {record.get('name', 'unknown')}: {str(e)}"
                )
                continue

        self.logger.info(
            f"Product entity creation complete - Created: {created_count}, Updated: {updated_count}"
        )

    async def _find_existing_product(self, pet_id: int) -> Optional[Product]:
        """
        Find existing Product entity by pet_id.

        Args:
            pet_id: The pet ID to search for

        Returns:
            Existing Product entity or None
        """
        try:
            entity_service = get_entity_service()

            # Search for products with matching pet_id
            from common.service.entity_service import SearchConditionRequest

            builder = SearchConditionRequest.builder()
            builder.equals("petId", str(pet_id))
            condition = builder.build()

            results = await entity_service.search(
                entity_class=Product.ENTITY_NAME,
                condition=condition,
                entity_version=str(Product.ENTITY_VERSION),
            )

            if results and len(results) > 0:
                # Return the first matching product
                product_data = results[0].data
                if hasattr(product_data, "model_dump"):
                    product_dict = product_data.model_dump(by_alias=True)
                else:
                    product_dict = product_data
                return Product(**product_dict)

        except Exception as e:
            self.logger.error(
                f"Error searching for existing product with pet_id {pet_id}: {str(e)}"
            )

        return None

    async def _create_new_product(self, record: Dict[str, Any]) -> Optional[Product]:
        """
        Create a new Product entity from extracted data.

        Args:
            record: Extracted pet data

        Returns:
            Created Product entity or None
        """
        try:
            # Create Product entity
            product = Product(
                pet_id=record.get("pet_id"),
                name=record["name"],
                category_id=record.get("category_id"),
                category_name=record.get("category_name"),
                status=record["status"],
                photo_urls=record.get("photo_urls", []),
                tags=record.get("tags", []),
                extracted_at=record.get("extracted_at"),
                # Initialize performance metrics with defaults
                sales_volume=0,
                revenue=0.0,
                inventory_count=10,  # Default inventory
                performance_score=None,
                trend_indicator=None,
                restock_needed=False,
            )

            # Save the product
            entity_service = get_entity_service()
            product_data = product.model_dump(by_alias=True)

            response = await entity_service.save(
                entity=product_data,
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )

            return product

        except Exception as e:
            self.logger.error(f"Error creating new product: {str(e)}")
            return None

    async def _update_existing_product(
        self, existing_product: Product, record: Dict[str, Any]
    ) -> Optional[Product]:
        """
        Update an existing Product entity with new data.

        Args:
            existing_product: The existing Product entity
            record: New extracted data

        Returns:
            Updated Product entity or None
        """
        try:
            # Update fields that might have changed
            existing_product.name = record["name"]
            existing_product.status = record["status"]
            existing_product.photo_urls = record.get("photo_urls", [])
            existing_product.tags = record.get("tags", [])
            existing_product.extracted_at = record.get("extracted_at")

            # Update category if provided
            if record.get("category_id"):
                existing_product.category_id = record["category_id"]
            if record.get("category_name"):
                existing_product.category_name = record["category_name"]

            # Save the updated product
            entity_service = get_entity_service()
            product_data = existing_product.model_dump(by_alias=True)

            response = await entity_service.update(
                entity_id=existing_product.technical_id or existing_product.entity_id,
                entity=product_data,
                entity_class=Product.ENTITY_NAME,
                entity_version=str(Product.ENTITY_VERSION),
            )

            return existing_product

        except Exception as e:
            self.logger.error(f"Error updating existing product: {str(e)}")
            return None
