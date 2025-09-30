"""
DataProcessingProcessor for Pet Store Performance Analysis System

Handles post-extraction processing of data including validation, cleanup,
and triggering of product analysis workflows.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from application.entity.product.version_1.product import Product
from services.services import get_entity_service


class DataProcessingProcessor(CyodaProcessor):
    """
    Processor for DataExtraction entity that handles post-extraction processing
    including data validation and triggering product analysis workflows.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataProcessingProcessor",
            description="Processes extracted data and triggers product analysis workflows",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the DataExtraction entity to handle post-extraction tasks.

        Args:
            entity: The DataExtraction entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with updated processing status
        """
        try:
            self.logger.info(
                f"Processing extracted data for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction = cast_entity(entity, DataExtraction)

            # Validate extraction was successful
            if extraction.execution_status != "completed":
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} is not in completed status"
                )
                return extraction

            # Process the extracted products
            await self._process_extracted_products(extraction)

            # Clean up old extraction data if needed
            await self._cleanup_old_data(extraction)

            # Update processing statistics
            self._update_processing_stats(extraction)

            self.logger.info(
                f"Data processing completed for extraction {extraction.technical_id}"
            )

            return extraction

        except Exception as e:
            self.logger.error(
                f"Error processing extracted data {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _process_extracted_products(self, extraction: DataExtraction) -> None:
        """
        Process products that were created from the extraction.

        Args:
            extraction: The DataExtraction entity
        """
        entity_service = get_entity_service()

        try:
            # Find products created from this extraction
            # We'll look for products in 'extracted' state that were created recently
            builder = SearchConditionRequest.builder()
            builder.equals("state", "extracted")
            condition = builder.build()

            products = await entity_service.search(
                entity_class=Product.ENTITY_NAME,
                condition=condition,
                entity_version=str(Product.ENTITY_VERSION),
            )

            processed_count = 0
            failed_count = 0

            for product_result in products:
                try:
                    product = cast_entity(product_result.data, Product)

                    # Trigger product validation and analysis workflow
                    # This will move the product through: extracted -> validated -> analyzed -> completed
                    await entity_service.execute_transition(
                        entity_id=product.technical_id or product.entity_id,
                        transition="validate",
                        entity_class=Product.ENTITY_NAME,
                        entity_version=str(Product.ENTITY_VERSION),
                    )

                    processed_count += 1
                    self.logger.debug(
                        f"Triggered analysis for product {product.technical_id}"
                    )

                except Exception as e:
                    failed_count += 1
                    self.logger.warning(f"Failed to process product: {str(e)}")
                    continue

            # Update extraction statistics
            extraction.processed_products = processed_count
            extraction.failed_products = failed_count

            self.logger.info(
                f"Processed {processed_count} products, {failed_count} failed for extraction {extraction.technical_id}"
            )

        except Exception as e:
            self.logger.error(f"Error processing extracted products: {str(e)}")
            extraction.add_extraction_error(f"Product processing failed: {str(e)}")

    async def _cleanup_old_data(self, extraction: DataExtraction) -> None:
        """
        Clean up old extraction data to prevent storage bloat.

        Args:
            extraction: The DataExtraction entity
        """
        try:
            # Clear the raw extracted data to save space
            # Keep only essential metadata
            if extraction.extracted_data:
                # Keep summary but remove raw data
                summary = {
                    "extraction_timestamp": extraction.extracted_data.get(
                        "extraction_timestamp"
                    ),
                    "total_items": len(extraction.extracted_data.get("pets", [])),
                    "data_cleared": True,
                }
                extraction.extracted_data = summary

                self.logger.debug(
                    f"Cleaned up raw data for extraction {extraction.technical_id}"
                )

        except Exception as e:
            self.logger.warning(f"Error cleaning up extraction data: {str(e)}")

    def _update_processing_stats(self, extraction: DataExtraction) -> None:
        """
        Update processing statistics for the extraction.

        Args:
            extraction: The DataExtraction entity to update
        """
        try:
            # Calculate success rate
            success_rate = extraction.calculate_success_rate()

            # Log processing summary
            self.logger.info(
                f"Extraction {extraction.technical_id} processing summary: "
                f"Success rate: {success_rate:.1f}%, "
                f"Processed: {extraction.processed_products or 0}, "
                f"Failed: {extraction.failed_products or 0}"
            )

            # Add processing completion timestamp
            from datetime import datetime, timezone

            processing_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            if not extraction.extracted_data:
                extraction.extracted_data = {}

            extraction.extracted_data["processing_completed"] = processing_timestamp
            extraction.extracted_data["success_rate"] = success_rate

        except Exception as e:
            self.logger.warning(f"Error updating processing stats: {str(e)}")
