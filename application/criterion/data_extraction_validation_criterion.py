"""
DataExtractionValidationCriterion for Pet Store Performance Analysis System

Validates that a DataExtraction entity meets all required business rules before it can
proceed to the execution stage as specified in functional requirements.
"""

from typing import Any

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class DataExtractionValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for DataExtraction entity that checks all business rules
    before the entity can proceed to execution stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionValidationCriterion",
            description="Validates DataExtraction business rules and configuration for Pet Store API access",
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
            extraction_job = cast_entity(entity, DataExtraction)

            # Validate required fields
            if not self._validate_required_fields(extraction_job):
                return False

            # Validate API configuration
            if not self._validate_api_configuration(extraction_job):
                return False

            # Validate business logic
            if not self._validate_business_logic(extraction_job):
                return False

            self.logger.info(
                f"DataExtraction entity {extraction_job.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating DataExtraction entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, extraction_job: DataExtraction) -> bool:
        """
        Validate that all required fields are present and valid.

        Args:
            extraction_job: The DataExtraction entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate job name
        if not extraction_job.job_name or len(extraction_job.job_name.strip()) == 0:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} has invalid job name: '{extraction_job.job_name}'"
            )
            return False

        if len(extraction_job.job_name) > 100:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} job name too long: {len(extraction_job.job_name)} characters"
            )
            return False

        # Validate job type
        if extraction_job.job_type not in DataExtraction.ALLOWED_JOB_TYPES:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} has invalid job type: {extraction_job.job_type}"
            )
            return False

        # Validate scheduled time
        if not extraction_job.scheduled_time:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} missing scheduled time"
            )
            return False

        return True

    def _validate_api_configuration(self, extraction_job: DataExtraction) -> bool:
        """
        Validate API configuration.

        Args:
            extraction_job: The DataExtraction entity to validate

        Returns:
            True if API configuration is valid, False otherwise
        """
        # Validate API base URL
        if not extraction_job.api_base_url:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} missing API base URL"
            )
            return False

        if not extraction_job.api_base_url.startswith(("http://", "https://")):
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} has invalid API base URL: {extraction_job.api_base_url}"
            )
            return False

        # Validate API endpoints
        if not extraction_job.api_endpoints or len(extraction_job.api_endpoints) == 0:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} has no API endpoints configured"
            )
            return False

        # Validate each endpoint
        for endpoint in extraction_job.api_endpoints:
            if not endpoint.startswith("/"):
                self.logger.warning(
                    f"DataExtraction {extraction_job.technical_id} has invalid endpoint: {endpoint} (should start with /)"
                )
                return False

        return True

    def _validate_business_logic(self, extraction_job: DataExtraction) -> bool:
        """
        Validate business logic rules.

        Args:
            extraction_job: The DataExtraction entity to validate

        Returns:
            True if business logic is valid, False otherwise
        """
        # Validate execution status
        if extraction_job.execution_status not in DataExtraction.ALLOWED_STATUSES:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} has invalid execution status: {extraction_job.execution_status}"
            )
            return False

        # Validate retry configuration
        if extraction_job.retry_count < 0:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} has negative retry count: {extraction_job.retry_count}"
            )
            return False

        if extraction_job.max_retries < 0:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} has negative max retries: {extraction_job.max_retries}"
            )
            return False

        if extraction_job.retry_count > extraction_job.max_retries:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} retry count ({extraction_job.retry_count}) exceeds max retries ({extraction_job.max_retries})"
            )
            return False

        # Validate that job is in a state that allows execution
        if extraction_job.execution_status not in ["PENDING", "FAILED"]:
            self.logger.warning(
                f"DataExtraction {extraction_job.technical_id} is not in a valid state for execution: {extraction_job.execution_status}"
            )
            return False

        # If job failed previously, check if retry is allowed
        if extraction_job.execution_status == "FAILED":
            if not extraction_job.is_ready_for_retry():
                self.logger.warning(
                    f"DataExtraction {extraction_job.technical_id} has exceeded maximum retry attempts"
                )
                return False

        return True
