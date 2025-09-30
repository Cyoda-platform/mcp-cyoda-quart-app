"""
DataExtractionValidationCriterion for Pet Store Performance Analysis System

Validates that a DataExtraction entity meets all required business rules before
it can proceed to the data extraction stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.data_extraction.version_1.data_extraction import DataExtraction


class DataExtractionValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for DataExtraction entity that checks all business rules
    before the entity can proceed to data extraction stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionValidationCriterion",
            description="Validates DataExtraction business rules and configuration",
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
            if not extraction.job_name or len(extraction.job_name.strip()) < 1:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid job name: '{extraction.job_name}'"
                )
                return False

            if not extraction.api_endpoint:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} missing API endpoint"
                )
                return False

            # Validate schedule configuration
            if extraction.schedule_type not in DataExtraction.ALLOWED_SCHEDULE_TYPES:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid schedule type: {extraction.schedule_type}"
                )
                return False

            if extraction.target_day not in DataExtraction.ALLOWED_DAYS:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid target day: {extraction.target_day}"
                )
                return False

            # Validate data format
            if extraction.data_format not in DataExtraction.ALLOWED_DATA_FORMATS:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid data format: {extraction.data_format}"
                )
                return False

            # Validate execution status
            if extraction.execution_status not in DataExtraction.ALLOWED_EXECUTION_STATUSES:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid execution status: {extraction.execution_status}"
                )
                return False

            # Validate API endpoint format
            if not extraction.api_endpoint.startswith(("http://", "https://")):
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid API endpoint format: {extraction.api_endpoint}"
                )
                return False

            # Validate retry count
            if extraction.retry_count < 0 or extraction.retry_count > 10:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid retry count: {extraction.retry_count}"
                )
                return False

            # Validate timeout
            if extraction.timeout_seconds < 30 or extraction.timeout_seconds > 3600:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has invalid timeout: {extraction.timeout_seconds}"
                )
                return False

            # Business logic validation
            # Check if extraction is due for execution (if scheduled)
            if extraction.execution_status == "pending" and not extraction.is_due_for_execution():
                self.logger.info(
                    f"DataExtraction {extraction.technical_id} is not yet due for execution"
                )
                # This is informational, not a validation failure
                # return False  # Uncomment if you want to prevent early execution

            # Check if extraction is already running
            if extraction.execution_status == "running":
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} is already running"
                )
                return False

            # Validate that we're not trying to run too frequently
            if extraction.last_execution:
                try:
                    from datetime import datetime, timezone, timedelta
                    last_exec = datetime.fromisoformat(extraction.last_execution.replace("Z", "+00:00"))
                    now = datetime.now(timezone.utc)
                    
                    # Prevent running more than once per hour
                    if (now - last_exec) < timedelta(hours=1):
                        self.logger.warning(
                            f"DataExtraction {extraction.technical_id} was executed too recently"
                        )
                        return False
                        
                except Exception as e:
                    self.logger.warning(
                        f"DataExtraction {extraction.technical_id} has invalid last execution timestamp: {str(e)}"
                    )
                    # Don't fail validation for timestamp parsing issues

            # Validate extraction hasn't failed too many times recently
            if extraction.extraction_errors and len(extraction.extraction_errors) > 5:
                self.logger.warning(
                    f"DataExtraction {extraction.technical_id} has too many recent errors: {len(extraction.extraction_errors)}"
                )
                # This is a warning but not a hard failure - allow retry

            self.logger.info(
                f"DataExtraction {extraction.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating DataExtraction entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
