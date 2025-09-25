"""
DataExtractionValidationCriterion for Pet Store Performance Analysis System

Validates that DataExtraction entities have successfully completed data collection
with acceptable quality and completeness as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.data_extraction.version_1.data_extraction import DataExtraction


class DataExtractionValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for DataExtraction entity that checks extraction success,
    data quality, and completeness before marking as completed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionValidationCriterion",
            description="Validates DataExtraction success and data quality",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the DataExtraction entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be DataExtraction)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating data extraction {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction = cast_entity(entity, DataExtraction)

            # Validate execution status
            if not self._validate_execution_status(extraction):
                return False

            # Validate extracted data
            if not self._validate_extracted_data(extraction):
                return False

            # Validate data quality
            if not self._validate_data_quality(extraction):
                return False

            # Validate extraction metrics
            if not self._validate_extraction_metrics(extraction):
                return False

            # Validate business rules
            if not self._validate_business_rules(extraction):
                return False

            self.logger.info(
                f"DataExtraction {extraction.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating data extraction {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_execution_status(self, extraction: DataExtraction) -> bool:
        """
        Validate that extraction execution completed successfully.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if execution status is valid, False otherwise
        """
        # Check execution status
        if extraction.execution_status != "COMPLETED":
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid execution status: {extraction.execution_status}"
            )
            return False

        # Check that execution timestamp exists
        if not extraction.last_execution_at:
            self.logger.warning(f"DataExtraction {extraction.technical_id} has no execution timestamp")
            return False

        # Check error count is acceptable
        error_count = extraction.error_count or 0
        if error_count > 5:  # Allow some errors but not too many
            self.logger.warning(f"DataExtraction {extraction.technical_id} has too many errors: {error_count}")
            return False

        return True

    def _validate_extracted_data(self, extraction: DataExtraction) -> bool:
        """
        Validate that extracted data exists and has reasonable content.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if extracted data is valid, False otherwise
        """
        # Check that data was extracted
        if not extraction.extracted_data:
            self.logger.warning(f"DataExtraction {extraction.technical_id} has no extracted data")
            return False

        # Check minimum number of products
        products_count = len(extraction.extracted_data)
        if products_count == 0:
            self.logger.warning(f"DataExtraction {extraction.technical_id} extracted no products")
            return False

        # Check maximum reasonable number (prevent data corruption)
        if products_count > 10000:
            self.logger.warning(f"DataExtraction {extraction.technical_id} extracted too many products: {products_count}")
            return False

        # Validate individual product records
        valid_products = 0
        for i, product in enumerate(extraction.extracted_data):
            if self._validate_product_record(product, i, extraction.technical_id):
                valid_products += 1

        # Require at least 80% of products to be valid
        valid_percentage = (valid_products / products_count) * 100
        if valid_percentage < 80.0:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has too many invalid products: "
                f"{valid_percentage:.1f}% valid"
            )
            return False

        return True

    def _validate_product_record(self, product: dict, index: int, extraction_id: str) -> bool:
        """
        Validate individual product record from extracted data.

        Args:
            product: Product data dictionary
            index: Index of product in the list
            extraction_id: DataExtraction technical ID for logging

        Returns:
            True if product record is valid, False otherwise
        """
        # Check required fields
        required_fields = ["id", "name", "category", "status"]
        for field in required_fields:
            if field not in product or not product[field]:
                self.logger.debug(f"DataExtraction {extraction_id} product[{index}] missing {field}")
                return False

        # Validate field formats
        try:
            # ID should be string
            if not isinstance(product["id"], (str, int)):
                return False

            # Name should be non-empty string
            if not isinstance(product["name"], str) or len(product["name"].strip()) == 0:
                return False

            # Category should be valid
            valid_categories = ["dog", "cat", "bird", "fish", "reptile", "small-pet"]
            if product["category"] not in valid_categories:
                return False

            # Status should be valid
            valid_statuses = ["available", "pending", "sold"]
            if product["status"] not in valid_statuses:
                return False

            # Validate numeric fields if present
            numeric_fields = ["price", "sales_volume", "inventory_level"]
            for field in numeric_fields:
                if field in product and product[field] is not None:
                    try:
                        value = float(product[field])
                        if value < 0:
                            return False
                    except (ValueError, TypeError):
                        return False

        except Exception:
            return False

        return True

    def _validate_data_quality(self, extraction: DataExtraction) -> bool:
        """
        Validate data quality metrics.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if data quality is acceptable, False otherwise
        """
        # Check data quality score
        quality_score = extraction.data_quality_score
        if quality_score is None:
            self.logger.warning(f"DataExtraction {extraction.technical_id} has no data quality score")
            return False

        # Require minimum quality score of 70%
        if quality_score < 70.0:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has low data quality score: {quality_score:.1f}%"
            )
            return False

        # Check extraction summary exists
        if not extraction.extraction_summary:
            self.logger.warning(f"DataExtraction {extraction.technical_id} has no extraction summary")
            return False

        return True

    def _validate_extraction_metrics(self, extraction: DataExtraction) -> bool:
        """
        Validate extraction performance metrics.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if metrics are reasonable, False otherwise
        """
        # Check products extracted count
        products_extracted = extraction.products_extracted or 0
        if products_extracted == 0:
            self.logger.warning(f"DataExtraction {extraction.technical_id} extracted no products")
            return False

        # Check extraction duration is reasonable
        duration_ms = extraction.extraction_duration_ms
        if duration_ms is None:
            self.logger.warning(f"DataExtraction {extraction.technical_id} has no duration recorded")
            return False

        # Duration should be reasonable (not too fast or too slow)
        if duration_ms < 100:  # Less than 100ms seems too fast
            self.logger.warning(f"DataExtraction {extraction.technical_id} completed too quickly: {duration_ms}ms")
            return False

        if duration_ms > 300000:  # More than 5 minutes seems too slow
            self.logger.warning(f"DataExtraction {extraction.technical_id} took too long: {duration_ms}ms")
            return False

        # Check consistency between products_extracted and actual data
        actual_count = len(extraction.extracted_data) if extraction.extracted_data else 0
        if products_extracted != actual_count:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has inconsistent product count: "
                f"Reported: {products_extracted}, Actual: {actual_count}"
            )
            return False

        return True

    def _validate_business_rules(self, extraction: DataExtraction) -> bool:
        """
        Validate business logic rules.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if business rules are satisfied, False otherwise
        """
        # Rule: Weekly extractions should have reasonable product counts
        if extraction.extraction_type == "WEEKLY":
            products_count = extraction.products_extracted or 0
            if products_count < 5:  # Too few for a pet store
                self.logger.warning(f"DataExtraction {extraction.technical_id} has too few products for weekly extraction: {products_count}")
                return False

        # Rule: Check retry count is not excessive
        retry_count = extraction.retry_count or 0
        if retry_count > 3:
            self.logger.warning(f"DataExtraction {extraction.technical_id} has excessive retry count: {retry_count}")
            return False

        # Rule: Validate extraction summary has expected structure
        if extraction.extraction_summary:
            summary = extraction.extraction_summary
            if "total_products" not in summary or "categories" not in summary:
                self.logger.warning(f"DataExtraction {extraction.technical_id} has invalid extraction summary structure")
                return False

            # Check that summary total matches actual count
            summary_total = summary.get("total_products", 0)
            actual_total = extraction.products_extracted or 0
            if summary_total != actual_total:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has inconsistent summary total: "
                    f"Summary: {summary_total}, Actual: {actual_total}"
                )
                return False

        return True
