"""
ApplicationRejectionProcessor for Purrfect Pets API

Rejects an adoption application after review.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.adoption_application.version_1.adoption_application import AdoptionApplication


class ApplicationRejectionProcessor(CyodaProcessor):
    """
    Processor for AdoptionApplication rejection that rejects an application after review.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationRejectionProcessor",
            description="Rejects an adoption application after review",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the AdoptionApplication rejection according to functional requirements.

        Args:
            entity: The AdoptionApplication entity to process (must be under review)
            **kwargs: Additional processing parameters (rejection reason, reviewer)

        Returns:
            The processed application entity in rejected state
        """
        try:
            self.logger.info(
                f"Processing AdoptionApplication rejection for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionApplication for type-safe operations
            application = cast_entity(entity, AdoptionApplication)

            # Get rejection information from kwargs
            rejection_reason = kwargs.get("rejectionReason") or kwargs.get("rejection_reason")
            reviewer = kwargs.get("reviewer")
            reviewer_id = kwargs.get("reviewerId") or kwargs.get("reviewer_id")

            # Validate application is currently under review
            if not application.is_under_review():
                raise ValueError("Application must be under review to reject")

            # Validate rejection reason is provided
            if not rejection_reason:
                raise ValueError("Rejection reason is required")

            # Set rejection date to current timestamp
            application.set_rejection_date()

            # Record rejection reason and reviewer
            application.rejection_reason = rejection_reason

            # Notify customer of rejection (in a real system)
            self.logger.info(
                f"Would notify customer {application.customer_id} of application rejection"
            )

            # Provide feedback for improvement (in a real system)
            # This would include suggestions for how the customer could improve their application
            self.logger.info(
                f"Would provide improvement feedback to customer {application.customer_id}"
            )

            # Log rejection activity
            reviewer_info = reviewer or reviewer_id or "Unknown reviewer"
            self.logger.info(
                f"AdoptionApplication {application.technical_id} rejected by {reviewer_info}. "
                f"Reason: {rejection_reason}"
            )

            return application

        except Exception as e:
            self.logger.error(
                f"Error processing application rejection {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
