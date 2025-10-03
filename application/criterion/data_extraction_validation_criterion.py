"""
DataExtractionValidationCriterion for Pet Store Performance Analysis System

Validates that a DataExtraction entity meets all required business rules before it can
be marked as completed as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.data_extraction.version_1.data_extraction import DataExtraction


class DataExtractionValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for DataExtraction entity that checks all business rules
    before the entity can be marked as completed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionValidationCriterion",
            description="Validates DataExtraction job completion and data quality",
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
                f"Validating DataExtraction entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction = cast_entity(entity, DataExtraction)

            # Validate extraction status
            if extraction.extraction_status != "completed":
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} not in completed status: {extraction.extraction_status}"
                )
                return False

            # Validate extraction was successful (no error message)
            if extraction.error_message:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has error: {extraction.error_message}"
                )
                return False

            # Validate timing data
            if not extraction.started_at or not extraction.completed_at:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} missing timing data"
                )
                return False

            # Validate extraction results
            if extraction.records_extracted is None or extraction.records_extracted < 0:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid records_extracted: {extraction.records_extracted}"
                )
                return False

            if extraction.records_processed is None or extraction.records_processed < 0:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid records_processed: {extraction.records_processed}"
                )
                return False

            # Validate data quality - at least 50% success rate required
            if extraction.records_extracted > 0:
                success_rate = (extraction.records_processed or 0) / extraction.records_extracted
                if success_rate < 0.5:
                    self.logger.warning(
                        f"DataExtraction {extraction.technical_id} has low success rate: {success_rate:.2%}"
                    )
                    return False

            # Validate data quality score if present
            if extraction.data_quality_score is not None:
                if extraction.data_quality_score < 50.0:
                    self.logger.warning(
                        f"DataExtraction {extraction.technical_id} has low data quality score: {extraction.data_quality_score}"
                    )
                    return False

            # Business logic validation - ensure meaningful extraction
            if extraction.records_extracted == 0:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} extracted no records"
                )
                return False

            # Validate job configuration
            if not extraction.job_name or len(extraction.job_name.strip()) == 0:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid job name"
                )
                return False

            if not extraction.api_endpoint:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has no API endpoint"
                )
                return False

            self.logger.info(
                f"DataExtraction {extraction.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating DataExtraction entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
