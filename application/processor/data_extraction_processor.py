"""
DataExtractionProcessor for Product Performance Analysis and Reporting System

Handles automated data extraction from Pet Store API, processes the retrieved data,
and creates Product entities for performance analysis.
"""

import asyncio
import logging
import random
from typing import Any, Dict, List
from urllib.parse import urljoin

import aiohttp

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from application.entity.product.version_1.product import Product
from services.services import get_entity_service


class DataExtractionProcessor(CyodaProcessor):
    """
    Processor for DataExtraction entity that fetches data from Pet Store API.
    
    Handles:
    - API connection and data retrieval
    - Data transformation and validation
    - Product entity creation from API data
    - Error handling and retry logic
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
        Execute data extraction from Pet Store API.

        Args:
            entity: The DataExtraction entity to process
            **kwargs: Additional processing parameters

        Returns:
            The updated DataExtraction entity with extraction results
        """
        try:
            self.logger.info(
                f"Starting data extraction {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction = cast_entity(entity, DataExtraction)

            # Start the extraction process
            extraction.start_extraction()

            # Extract data from Pet Store API
            extracted_data = await self._extract_from_api(extraction)
            
            # Process and create Product entities
            products_created = await self._process_extracted_data(extracted_data, extraction)
            
            # Complete the extraction
            extraction.complete_extraction(
                records_extracted=len(extracted_data),
                records_processed=products_created
            )

            self.logger.info(
                f"Data extraction {extraction.technical_id} completed successfully - "
                f"Extracted: {len(extracted_data)}, Processed: {products_created}"
            )

            return extraction

        except Exception as e:
            self.logger.error(
                f"Error in data extraction {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            
            # Cast again for error handling
            extraction = cast_entity(entity, DataExtraction)
            extraction.fail_extraction(str(e))
            
            raise

    async def _extract_from_api(self, extraction: DataExtraction) -> List[Dict[str, Any]]:
        """
        Extract data from Pet Store API endpoints.
        
        Args:
            extraction: The DataExtraction entity with API configuration
            
        Returns:
            List of extracted data records
        """
        all_data = []
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=extraction.timeout_seconds)
        ) as session:
            
            for endpoint in extraction.api_endpoints:
                try:
                    url = urljoin(extraction.api_url, endpoint)
                    self.logger.info(f"Fetching data from {url}")
                    
                    start_time = asyncio.get_event_loop().time()
                    
                    async with session.get(url) as response:
                        response_time = (asyncio.get_event_loop().time() - start_time) * 1000
                        extraction.api_response_time = response_time
                        extraction.api_status_code = response.status
                        
                        if response.status == 200:
                            if extraction.data_format == "json":
                                data = await response.json()
                            else:
                                # Handle XML format if needed
                                text_data = await response.text()
                                data = {"raw_data": text_data}
                            
                            # Process different endpoint types
                            processed_data = self._process_endpoint_data(endpoint, data)
                            all_data.extend(processed_data)
                            
                        else:
                            self.logger.warning(
                                f"API endpoint {url} returned status {response.status}"
                            )
                            
                except Exception as e:
                    self.logger.error(f"Error fetching from {endpoint}: {str(e)}")
                    extraction.error_count += 1
                    if extraction.error_messages is None:
                        extraction.error_messages = []
                    extraction.error_messages.append(f"Endpoint {endpoint}: {str(e)}")
        
        return all_data

    def _process_endpoint_data(self, endpoint: str, data: Any) -> List[Dict[str, Any]]:
        """
        Process data from specific API endpoints.
        
        Args:
            endpoint: The API endpoint that provided the data
            data: Raw data from the API
            
        Returns:
            List of processed data records
        """
        processed_records = []
        
        if "/store/inventory" in endpoint:
            # Process inventory data
            if isinstance(data, dict):
                for status, count in data.items():
                    processed_records.append({
                        "name": f"Pet Status: {status}",
                        "category": "General",
                        "status": status,
                        "stock_level": count,
                        "api_source": "petstore_inventory"
                    })
        
        elif "/pet/findByStatus" in endpoint:
            # Process pet data
            if isinstance(data, list):
                for pet in data:
                    if isinstance(pet, dict):
                        processed_records.append(self._transform_pet_data(pet))
        
        return processed_records

    def _transform_pet_data(self, pet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform pet data from API to Product entity format.
        
        Args:
            pet_data: Raw pet data from API
            
        Returns:
            Transformed data for Product entity
        """
        # Extract category information
        category = "General"
        if "category" in pet_data and isinstance(pet_data["category"], dict):
            category = pet_data["category"].get("name", "General")
        
        # Generate mock sales and pricing data for analysis
        # In a real system, this would come from actual sales data
        mock_price = self._generate_mock_price(category)
        mock_sales = self._generate_mock_sales()
        
        return {
            "name": pet_data.get("name", "Unknown Pet"),
            "category": category,
            "status": pet_data.get("status", "available"),
            "price": mock_price,
            "sales_volume": mock_sales,
            "stock_level": self._generate_mock_stock(),
            "reorder_point": 10,  # Default reorder point
            "api_id": str(pet_data.get("id", "")),
            "api_source": "petstore_pets"
        }

    def _generate_mock_price(self, category: str) -> float:
        """Generate mock pricing data based on category"""
        category_prices = {
            "Dogs": 150.0,
            "Cats": 120.0,
            "Fish": 25.0,
            "Birds": 80.0,
            "Reptiles": 200.0,
            "Small Pets": 45.0
        }
        return category_prices.get(category, 75.0)

    def _generate_mock_sales(self) -> int:
        """Generate mock sales volume data"""
        return random.randint(5, 100)

    def _generate_mock_stock(self) -> int:
        """Generate mock stock level data"""
        return random.randint(0, 50)

    async def _process_extracted_data(
        self, 
        extracted_data: List[Dict[str, Any]], 
        extraction: DataExtraction
    ) -> int:
        """
        Process extracted data and create Product entities.
        
        Args:
            extracted_data: List of extracted data records
            extraction: The DataExtraction entity
            
        Returns:
            Number of Product entities successfully created
        """
        entity_service = get_entity_service()
        products_created = 0
        
        for record in extracted_data:
            try:
                # Create Product entity from extracted data
                product = Product(**record)
                
                # Convert to dict for EntityService
                product_data = product.model_dump(by_alias=True)
                
                # Save the Product entity
                response = await entity_service.save(
                    entity=product_data,
                    entity_class=Product.ENTITY_NAME,
                    entity_version=str(Product.ENTITY_VERSION),
                )
                
                products_created += 1
                
                self.logger.info(
                    f"Created Product entity {response.metadata.id} from extracted data"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to create Product from data {record}: {str(e)}")
                extraction.records_failed = (extraction.records_failed or 0) + 1
                continue
        
        return products_created
