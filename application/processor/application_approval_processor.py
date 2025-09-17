"""
ApplicationApprovalProcessor for Purrfect Pets API

Approves an adoption application after successful review.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.adoption_application.version_1.adoption_application import AdoptionApplication


class ApplicationApprovalProcessor(CyodaProcessor):
    """
    Processor for AdoptionApplication approval that approves an application after review.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationApprovalProcessor",
            description="Approves an adoption application after successful review",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the AdoptionApplication approval according to functional requirements.

        Args:
            entity: The AdoptionApplication entity to process (must be under review)
            **kwargs: Additional processing parameters (approval notes, reviewer)

        Returns:
            The processed application entity in approved state
        """
        try:
            self.logger.info(
                f"Processing AdoptionApplication approval for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionApplication for type-safe operations
            application = cast_entity(entity, AdoptionApplication)

            # Get approval information from kwargs
            approval_notes = kwargs.get("approvalNotes") or kwargs.get("approval_notes")
            reviewer = kwargs.get("reviewer")
            reviewer_id = kwargs.get("reviewerId") or kwargs.get("reviewer_id")

            # Validate application is currently under review
            if not application.is_under_review():
                raise ValueError("Application must be under review to approve")

            # Validate all approval criteria are met (placeholder)
            self._validate_approval_criteria(kwargs)

            # Set approval date to current timestamp
            application.set_approval_date()

            # Record approval notes and reviewer
            if approval_notes:
                application.review_notes = approval_notes

            # Notify customer of approval (in a real system)
            self.logger.info(
                f"Would notify customer {application.customer_id} of application approval"
            )

            # Create pet reservation for customer (in a real system)
            # This would trigger the pet reservation process
            self.logger.info(
                f"Would create pet reservation for customer {application.customer_id} "
                f"and pet {application.pet_id}"
            )

            # Log approval activity
            reviewer_info = reviewer or reviewer_id or "Unknown reviewer"
            self.logger.info(
                f"AdoptionApplication {application.technical_id} approved by {reviewer_info}"
            )

            return application

        except Exception as e:
            self.logger.error(
                f"Error processing application approval {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_approval_criteria(self, kwargs: dict) -> None:
        """
        Validate that all approval criteria are met.

        Args:
            kwargs: Additional parameters containing approval criteria

        Raises:
            ValueError: If approval criteria are not met
        """
        # Background check must pass
        background_check_passed = kwargs.get("backgroundCheckPassed") or kwargs.get("background_check_passed")
        if not background_check_passed:
            raise ValueError("Background check must pass for approval")

        # References must be verified
        references_verified = kwargs.get("referencesVerified") or kwargs.get("references_verified")
        if not references_verified:
            raise ValueError("References must be verified for approval")

        # Housing must be approved
        housing_approved = kwargs.get("housingApproved") or kwargs.get("housing_approved")
        if not housing_approved:
            raise ValueError("Housing situation must be approved")

        # Customer must not be blacklisted
        customer_blacklisted = kwargs.get("customerBlacklisted") or kwargs.get("customer_blacklisted")
        if customer_blacklisted:
            raise ValueError("Cannot approve application for blacklisted customer")

        # Pet compatibility must be confirmed
        pet_compatibility_confirmed = kwargs.get("petCompatibilityConfirmed") or kwargs.get("pet_compatibility_confirmed")
        if not pet_compatibility_confirmed:
            raise ValueError("Pet compatibility must be confirmed for approval")

        self.logger.debug("All approval criteria validation passed")
