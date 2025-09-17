"""
ApplicationReviewStartProcessor for Purrfect Pets API

Starts the review process for a submitted application.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.adoption_application.version_1.adoption_application import (
    AdoptionApplication,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ApplicationReviewStartProcessor(CyodaProcessor):
    """
    Processor for AdoptionApplication review start that begins the review process.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationReviewStartProcessor",
            description="Starts the review process for a submitted application",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the AdoptionApplication review start according to functional requirements.

        Args:
            entity: The AdoptionApplication entity to process (must be submitted)
            **kwargs: Additional processing parameters (reviewer information)

        Returns:
            The processed application entity in under_review state
        """
        try:
            self.logger.info(
                f"Processing AdoptionApplication review start for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionApplication for type-safe operations
            application = cast_entity(entity, AdoptionApplication)

            # Get reviewer information from kwargs
            reviewer_info = kwargs.get("reviewerInfo") or kwargs.get("reviewer_info")
            reviewer_id = kwargs.get("reviewerId") or kwargs.get("reviewer_id")
            reviewer_name = kwargs.get("reviewerName") or kwargs.get("reviewer_name")

            # Validate application is currently submitted
            if not application.is_submitted():
                raise ValueError("Application must be submitted to start review")

            # Assign reviewer to application (in a real system)
            # This would create a reviewer assignment record
            if reviewer_id or reviewer_name:
                reviewer_assignment = (
                    f"Assigned to reviewer: {reviewer_name or reviewer_id}"
                )
                self.logger.info(
                    f"Application {application.technical_id} - {reviewer_assignment}"
                )

            # Set review start date to current timestamp (placeholder)
            # In a real system, you might have a review_start_date field
            review_start_time = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Create review tracking record (in a real system)
            # This would create a separate ReviewTracking entity
            self.logger.info(
                f"Would create review tracking record for application {application.technical_id} "
                f"starting at {review_start_time}"
            )

            # Notify customer that review has started (in a real system)
            self.logger.info(
                f"Would notify customer {application.customer_id} that review has started "
                f"for application {application.technical_id}"
            )

            # Log review start activity
            self.logger.info(
                f"AdoptionApplication {application.technical_id} review started"
            )

            return application

        except Exception as e:
            self.logger.error(
                f"Error processing application review start {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
