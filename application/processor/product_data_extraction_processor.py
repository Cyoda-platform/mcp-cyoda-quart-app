"""
ProductDataExtractionProcessor for Product Performance Analysis and Reporting System

Handles data extraction from the Pet Store API, creates Product entities,
and tracks extraction metrics as specified in functional requirements.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from application.entity.product.version_1.product import Product
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ProductDataExtractionProcessor(CyodaProcessor):
    """
    Processor for extracting product data from Pet Store API.

    Fetches product information, creates/updates Product entities,
    and tracks extraction metrics and status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ProductDataExtractionProcessor",
            description="Extracts product data from Pet Store API and creates Product entities",
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
            The processed DataExtraction entity with results
        """
        try:
            self.logger.info(
                f"Starting data extraction {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction_entity = cast_entity(entity, DataExtraction)

            # Mark extraction as started
            extraction_entity.mark_started()

            # Perform the data extraction
            extraction_results = await self._extract_pet_store_data(extraction_entity)

            # Update extraction entity with results
            self._update_extraction_results(extraction_entity, extraction_results)

            # Mark extraction as completed
            extraction_entity.mark_completed(success=extraction_results["success"])

            self.logger.info(
                f"Data extraction {extraction_entity.technical_id} completed successfully. "
                f"Extracted {extraction_results.get('products_created', 0)} products."
            )

            return extraction_entity

        except Exception as e:
            self.logger.error(
                f"Error in data extraction {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )

            # Update entity with error information
            if hasattr(entity, "add_error"):
                entity.add_error(
                    str(e), {"processor": "ProductDataExtractionProcessor"}
                )

            raise

    async def _extract_pet_store_data(
        self, extraction_entity: DataExtraction
    ) -> Dict[str, Any]:
        """
        Extract data from Pet Store API.

        Args:
            extraction_entity: The DataExtraction entity

        Returns:
            Dictionary containing extraction results
        """
        results = {
            "success": False,
            "products_created": 0,
            "products_updated": 0,
            "records_extracted": 0,
            "records_failed": 0,
            "api_calls": [],
        }

        try:
            # Get entity service for creating Product entities
            entity_service = get_entity_service()

            # Extract products from Pet Store API
            products_data = await self._fetch_products_from_api(extraction_entity)
            results["records_extracted"] = len(products_data)

            # Process each product
            for product_data in products_data:
                try:
                    # Create Product entity
                    product_entity = self._create_product_entity(product_data)

                    # Save the Product entity
                    response = await entity_service.save(
                        entity=product_entity.model_dump(by_alias=True),
                        entity_class=Product.ENTITY_NAME,
                        entity_version=str(Product.ENTITY_VERSION),
                    )

                    current_count = results.get("products_created", 0)
                    results["products_created"] = current_count + 1

                    self.logger.debug(
                        f"Created Product entity {response.metadata.id} for {product_data.get('name', 'Unknown')}"
                    )

                except Exception as e:
                    self.logger.warning(f"Failed to create Product entity: {str(e)}")
                    current_failed = results.get("records_failed", 0)
                    results["records_failed"] = current_failed + 1
                    continue

            results["success"] = True
            return results

        except Exception as e:
            self.logger.error(f"Failed to extract data from Pet Store API: {str(e)}")
            results["success"] = False
            raise

    async def _fetch_products_from_api(
        self, extraction_entity: DataExtraction
    ) -> List[Dict[str, Any]]:
        """
        Fetch products from Pet Store API.

        Args:
            extraction_entity: The DataExtraction entity

        Returns:
            List of product data dictionaries
        """
        products = []
        base_url = extraction_entity.source_url or "https://petstore.swagger.io/v2"

        # Pet Store API endpoints to call
        endpoints = [
            f"{base_url}/pet/findByStatus?status=available",
            f"{base_url}/pet/findByStatus?status=pending",
            f"{base_url}/pet/findByStatus?status=sold",
        ]

        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    self.logger.info(f"Calling Pet Store API: {endpoint}")

                    timeout = aiohttp.ClientTimeout(total=30)
                    async with session.get(endpoint, timeout=timeout) as response:
                        # Record API call
                        extraction_entity.add_api_call(endpoint, response.status)

                        if response.status == 200:
                            data = await response.json()

                            # Process the response data
                            if isinstance(data, list):
                                for item in data:
                                    product_data = self._transform_api_data(item)
                                    if product_data:
                                        products.append(product_data)

                            self.logger.info(
                                f"Successfully fetched {len(data) if isinstance(data, list) else 0} items from {endpoint}"
                            )
                        else:
                            self.logger.warning(
                                f"API call failed with status {response.status}: {endpoint}"
                            )

                except asyncio.TimeoutError:
                    self.logger.warning(f"Timeout calling API endpoint: {endpoint}")
                    extraction_entity.add_api_call(endpoint, 408)  # Request Timeout
                except Exception as e:
                    self.logger.warning(
                        f"Error calling API endpoint {endpoint}: {str(e)}"
                    )
                    extraction_entity.add_api_call(
                        endpoint, 500
                    )  # Internal Server Error

        self.logger.info(f"Total products extracted: {len(products)}")
        return products

    def _transform_api_data(self, api_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform Pet Store API data to Product entity format.

        Args:
            api_data: Raw data from Pet Store API

        Returns:
            Transformed product data or None if invalid
        """
        try:
            # Extract basic product information
            product_data = {
                "name": api_data.get("name", "Unknown Product"),
                "status": api_data.get("status", "available"),
                "pet_store_id": str(api_data.get("id", "")),
                "extraction_source": "pet_store_api",
            }

            # Extract category information
            category_info = api_data.get("category", {})
            if isinstance(category_info, dict):
                product_data["category"] = category_info.get("name", "Unknown")
            else:
                product_data["category"] = "Unknown"

            # Set default values for missing fields
            product_data["price"] = None  # Pet Store API doesn't provide price
            product_data["inventory_level"] = (
                None  # Pet Store API doesn't provide inventory
            )

            # Update extraction timestamp
            product_data["extracted_at"] = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            return product_data

        except Exception as e:
            self.logger.warning(f"Failed to transform API data: {str(e)}")
            return None

    def _create_product_entity(self, product_data: Dict[str, Any]) -> Product:
        """
        Create a Product entity from transformed data.

        Args:
            product_data: Transformed product data

        Returns:
            Product entity instance
        """
        return Product(**product_data)

    def _update_extraction_results(
        self, extraction_entity: DataExtraction, results: Dict[str, Any]
    ) -> None:
        """
        Update the DataExtraction entity with extraction results.

        Args:
            extraction_entity: The DataExtraction entity to update
            results: Extraction results dictionary
        """
        extraction_entity.records_extracted = results.get("records_extracted", 0)
        extraction_entity.records_failed = results.get("records_failed", 0)
        extraction_entity.products_created = results.get("products_created", 0)
        extraction_entity.products_updated = results.get("products_updated", 0)

        # Calculate data quality score
        total_records = (
            extraction_entity.records_extracted + extraction_entity.records_failed
        )
        if total_records > 0:
            success_rate = extraction_entity.records_extracted / total_records
            extraction_entity.data_quality_score = success_rate * 100
        else:
            extraction_entity.data_quality_score = 0.0
