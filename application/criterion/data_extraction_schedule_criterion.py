"""
DataExtractionScheduleCriterion for Product Performance Analysis and Reporting System

Validates that a DataExtraction entity is scheduled to run and meets
timing requirements for automated data extraction.
"""

from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity

from application.entity.data_extraction.version_1.data_extraction import DataExtraction


class DataExtractionScheduleCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for DataExtraction entity to check if it should be executed.
    
    Ensures the data extraction is scheduled for the current time and meets
    all requirements for automated execution.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DataExtractionScheduleCriterion",
            description="Validates that DataExtraction entity is ready for execution based on schedule",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the data extraction entity should be executed now.

        Args:
            entity: The CyodaEntity to validate (expected to be DataExtraction)
            **kwargs: Additional criteria parameters

        Returns:
            True if the extraction should be executed, False otherwise
        """
        try:
            self.logger.info(
                f"Validating extraction schedule for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to DataExtraction for type-safe operations
            extraction_entity = cast_entity(entity, DataExtraction)

            # Check if extraction is scheduled for execution
            if not self._is_scheduled_for_execution(extraction_entity):
                self.logger.debug(
                    f"Extraction {extraction_entity.technical_id} is not scheduled for execution"
                )
                return False

            # Check if extraction source is valid
            if not self._has_valid_source(extraction_entity):
                self.logger.warning(
                    f"Extraction {extraction_entity.technical_id} has invalid source configuration"
                )
                return False

            # Check if extraction hasn't exceeded retry limits
            if not self._within_retry_limits(extraction_entity):
                self.logger.warning(
                    f"Extraction {extraction_entity.technical_id} has exceeded retry limits"
                )
                return False

            # Check if extraction type is supported
            if not self._is_supported_extraction_type(extraction_entity):
                self.logger.warning(
                    f"Extraction {extraction_entity.technical_id} has unsupported extraction type"
                )
                return False

            self.logger.info(
                f"Extraction {extraction_entity.technical_id} passed all schedule criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating extraction schedule {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _is_scheduled_for_execution(self, extraction: DataExtraction) -> bool:
        """
        Check if extraction is scheduled for execution.

        Args:
            extraction: The DataExtraction entity to check

        Returns:
            True if extraction should be executed, False otherwise
        """
        current_time = datetime.now(timezone.utc)
        
        # Check if scheduled_for is set
        if not extraction.scheduled_for:
            # If no specific schedule, check schedule pattern
            return self._check_schedule_pattern(extraction, current_time)
        
        try:
            # Parse scheduled time
            scheduled_time = datetime.fromisoformat(extraction.scheduled_for.replace("Z", "+00:00"))
            
            # Check if current time is past scheduled time (within 1 hour window)
            time_diff = (current_time - scheduled_time).total_seconds()
            
            # Allow execution if within 1 hour of scheduled time
            if 0 <= time_diff <= 3600:  # 0 to 1 hour past scheduled time
                self.logger.debug(f"Extraction scheduled for {scheduled_time}, current time {current_time}")
                return True
            
            self.logger.debug(f"Extraction not in execution window. Scheduled: {scheduled_time}, Current: {current_time}")
            return False
            
        except Exception as e:
            self.logger.warning(f"Failed to parse scheduled time: {str(e)}")
            return False

    def _check_schedule_pattern(self, extraction: DataExtraction, current_time: datetime) -> bool:
        """
        Check if extraction should run based on schedule pattern.

        Args:
            extraction: The DataExtraction entity
            current_time: Current timestamp

        Returns:
            True if extraction should run based on pattern, False otherwise
        """
        pattern = extraction.schedule_pattern
        
        if pattern == "manual":
            # Manual extractions don't run automatically
            return False
        
        elif pattern == "weekly_monday":
            # Run on Mondays (weekday 0)
            is_monday = current_time.weekday() == 0
            
            # Check if it's within business hours (8 AM to 6 PM UTC)
            is_business_hours = 8 <= current_time.hour <= 18
            
            self.logger.debug(f"Monday check: {is_monday}, Business hours: {is_business_hours}")
            return is_monday and is_business_hours
        
        elif pattern == "daily":
            # Run daily during business hours
            is_business_hours = 8 <= current_time.hour <= 18
            return is_business_hours
        
        elif pattern == "weekly":
            # Run weekly on Mondays
            return current_time.weekday() == 0
        
        elif pattern == "monthly":
            # Run on the first day of the month
            return current_time.day == 1
        
        else:
            self.logger.warning(f"Unknown schedule pattern: {pattern}")
            return False

    def _has_valid_source(self, extraction: DataExtraction) -> bool:
        """
        Check if extraction has valid source configuration.

        Args:
            extraction: The DataExtraction entity to check

        Returns:
            True if source is valid, False otherwise
        """
        # Check if source URL is set
        if not extraction.source_url:
            self.logger.debug("Extraction missing source URL")
            return False

        # Check if source URL is valid format
        if not extraction.source_url.startswith(("http://", "https://")):
            self.logger.debug("Extraction source URL is not a valid HTTP/HTTPS URL")
            return False

        # Check if extraction type is set
        if not extraction.extraction_type:
            self.logger.debug("Extraction missing extraction type")
            return False

        return True

    def _within_retry_limits(self, extraction: DataExtraction) -> bool:
        """
        Check if extraction is within retry limits.

        Args:
            extraction: The DataExtraction entity to check

        Returns:
            True if within retry limits, False otherwise
        """
        retry_count = extraction.retry_count or 0
        max_retries = extraction.max_retries or 3
        
        if retry_count >= max_retries:
            self.logger.debug(f"Extraction has exceeded retry limits: {retry_count}/{max_retries}")
            return False
        
        return True

    def _is_supported_extraction_type(self, extraction: DataExtraction) -> bool:
        """
        Check if extraction type is supported.

        Args:
            extraction: The DataExtraction entity to check

        Returns:
            True if extraction type is supported, False otherwise
        """
        supported_types = [
            "pet_store_products",
            "inventory_update", 
            "price_update",
            "full_sync"
        ]
        
        if extraction.extraction_type not in supported_types:
            self.logger.debug(f"Unsupported extraction type: {extraction.extraction_type}")
            return False
        
        return True
