"""
DataExtractionValidationCriterion for Product Performance Analysis and Reporting System

Validates DataExtraction entities to ensure proper API configuration and extraction settings
before proceeding to data extraction from Pet Store API.
"""

from typing import Any
from urllib.parse import urlparse

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class DataExtractionValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for DataExtraction entity that checks API configuration and settings.

    Validates:
    - API configuration and endpoints
    - Extraction settings and parameters
    - Schedule and timing configuration
    - Error handling settings
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionValidationCriterion",
            description="Validates DataExtraction entity API configuration and settings",
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

            # Validate required fields
            if not self._validate_required_fields(extraction):
                return False

            # Validate API configuration
            if not self._validate_api_configuration(extraction):
                return False

            # Validate extraction settings
            if not self._validate_extraction_settings(extraction):
                return False

            # Validate schedule configuration
            if not self._validate_schedule_configuration(extraction):
                return False

            self.logger.info(
                f"DataExtraction entity {extraction.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating DataExtraction entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, extraction: DataExtraction) -> bool:
        """
        Validate that all required fields are present and valid.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate job name
        if not extraction.job_name or len(extraction.job_name.strip()) == 0:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid job name: '{extraction.job_name}'"
            )
            return False

        if len(extraction.job_name) > 100:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} job name too long: {len(extraction.job_name)} characters"
            )
            return False

        # Validate extraction type
        if (
            not extraction.extraction_type
            or extraction.extraction_type not in extraction.ALLOWED_EXTRACTION_TYPES
        ):
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid extraction type: '{extraction.extraction_type}'"
            )
            return False

        # Validate status
        if (
            not extraction.status
            or extraction.status not in extraction.ALLOWED_STATUSES
        ):
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid status: '{extraction.status}'"
            )
            return False

        # Validate data format
        if (
            not extraction.data_format
            or extraction.data_format not in extraction.ALLOWED_DATA_FORMATS
        ):
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid data format: '{extraction.data_format}'"
            )
            return False

        return True

    def _validate_api_configuration(self, extraction: DataExtraction) -> bool:
        """
        Validate API configuration and endpoints.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if API configuration is valid, False otherwise
        """
        # Validate API URL
        if not extraction.api_url:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has empty API URL"
            )
            return False

        # Validate URL format
        try:
            parsed_url = urlparse(extraction.api_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid API URL format: {extraction.api_url}"
                )
                return False

            # Ensure HTTPS for security (allow HTTP for development)
            if parsed_url.scheme not in ["http", "https"]:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has unsupported URL scheme: {parsed_url.scheme}"
                )
                return False

        except Exception as e:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has malformed API URL: {str(e)}"
            )
            return False

        # Validate API endpoints
        if not extraction.api_endpoints or len(extraction.api_endpoints) == 0:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has no API endpoints configured"
            )
            return False

        # Validate each endpoint
        for endpoint in extraction.api_endpoints:
            if not endpoint or len(endpoint.strip()) == 0:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has empty endpoint"
                )
                return False

            # Endpoint should start with /
            if not endpoint.startswith("/"):
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid endpoint format: {endpoint}"
                )
                return False

        return True

    def _validate_extraction_settings(self, extraction: DataExtraction) -> bool:
        """
        Validate extraction settings and parameters.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if extraction settings are valid, False otherwise
        """
        # Validate timeout
        if (
            extraction.timeout_seconds <= 0 or extraction.timeout_seconds > 3600
        ):  # Max 1 hour
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid timeout: {extraction.timeout_seconds} seconds"
            )
            return False

        # Validate retry settings
        if (
            extraction.max_retries < 0 or extraction.max_retries > 10
        ):  # Reasonable limit
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid max retries: {extraction.max_retries}"
            )
            return False

        if (
            extraction.retry_count < 0
            or extraction.retry_count > extraction.max_retries
        ):
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid retry count: {extraction.retry_count}"
            )
            return False

        # Validate error count
        if extraction.error_count < 0:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has negative error count: {extraction.error_count}"
            )
            return False

        # Validate record counts if present
        if (
            extraction.records_extracted is not None
            and extraction.records_extracted < 0
        ):
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has negative records extracted: {extraction.records_extracted}"
            )
            return False

        if (
            extraction.records_processed is not None
            and extraction.records_processed < 0
        ):
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has negative records processed: {extraction.records_processed}"
            )
            return False

        if extraction.records_failed is not None and extraction.records_failed < 0:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has negative records failed: {extraction.records_failed}"
            )
            return False

        # Validate data quality score if present
        if extraction.data_quality_score is not None and (
            extraction.data_quality_score < 0 or extraction.data_quality_score > 100
        ):
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid data quality score: {extraction.data_quality_score}"
            )
            return False

        # Validate API response metrics if present
        if (
            extraction.api_response_time is not None
            and extraction.api_response_time < 0
        ):
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has negative API response time: {extraction.api_response_time}"
            )
            return False

        if extraction.api_status_code is not None:
            if extraction.api_status_code < 100 or extraction.api_status_code > 599:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid API status code: {extraction.api_status_code}"
                )
                return False

        return True

    def _validate_schedule_configuration(self, extraction: DataExtraction) -> bool:
        """
        Validate schedule and timing configuration.

        Args:
            extraction: The DataExtraction entity to validate

        Returns:
            True if schedule configuration is valid, False otherwise
        """
        # Validate schedule format
        valid_schedules = ["weekly_monday", "daily", "monthly", "on_demand", "manual"]

        if extraction.schedule not in valid_schedules:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has invalid schedule: {extraction.schedule}"
            )
            return False

        # Validate timestamps if present
        timestamp_fields = [
            extraction.started_at,
            extraction.completed_at,
            extraction.next_scheduled_run,
            extraction.last_successful_run,
            extraction.created_at,
            extraction.updated_at,
        ]

        for timestamp in timestamp_fields:
            if timestamp is not None:
                if not self._validate_timestamp_format(timestamp):
                    self.logger.warning(
                        f"DataExtraction {extraction.technical_id} has invalid timestamp format: {timestamp}"
                    )
                    return False

        # Validate duration if present
        if extraction.duration_seconds is not None and extraction.duration_seconds < 0:
            self.logger.warning(
                f"DataExtraction {extraction.technical_id} has negative duration: {extraction.duration_seconds}"
            )
            return False

        # Validate logical consistency of timestamps
        if extraction.started_at is not None and extraction.completed_at is not None:
            try:
                from datetime import datetime

                start_time = datetime.fromisoformat(
                    extraction.started_at.replace("Z", "+00:00")
                )
                end_time = datetime.fromisoformat(
                    extraction.completed_at.replace("Z", "+00:00")
                )

                if start_time >= end_time:
                    self.logger.warning(
                        f"DataExtraction {extraction.technical_id} has invalid time range: "
                        f"start {extraction.started_at} >= end {extraction.completed_at}"
                    )
                    return False

            except (ValueError, AttributeError) as e:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid timestamp format: {str(e)}"
                )
                return False

        return True

    def _validate_timestamp_format(self, timestamp: str) -> bool:
        """
        Validate ISO 8601 timestamp format.

        Args:
            timestamp: Timestamp string to validate

        Returns:
            True if format is valid, False otherwise
        """
        try:
            from datetime import datetime

            # Try to parse ISO format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return True
        except (ValueError, AttributeError):
            return False
