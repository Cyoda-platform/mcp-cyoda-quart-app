"""
ApplicationExpirationProcessor for Purrfect Pets API

Expires an adoption application that has been inactive too long.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.adoption_application.version_1.adoption_application import (
    AdoptionApplication,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ApplicationExpirationProcessor(CyodaProcessor):
    """
    Processor for AdoptionApplication expiration that expires inactive applications.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationExpirationProcessor",
            description="Expires an adoption application that has been inactive too long",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the AdoptionApplication expiration according to functional requirements.

        Args:
            entity: The AdoptionApplication entity to process (must be submitted or under review)
            **kwargs: Additional processing parameters (expiration reason)

        Returns:
            The processed application entity in expired state
        """
        try:
            self.logger.info(
                f"Processing AdoptionApplication expiration for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionApplication for type-safe operations
            application = cast_entity(entity, AdoptionApplication)

            # Get expiration information from kwargs
            expiration_reason = kwargs.get("expirationReason") or kwargs.get(
                "expiration_reason"
            )
            days_inactive = kwargs.get("daysInactive") or kwargs.get("days_inactive")

            # Validate application is in a state that can expire
            if (
                application.is_approved()
                or application.is_rejected()
                or application.is_expired()
            ):
                raise ValueError("Application cannot be expired from current state")

            # Validate expiration criteria
            self._validate_expiration_criteria(application, kwargs)

            # Set expiration reason (default if not provided)
            if not expiration_reason:
                expiration_reason = f"Application expired due to inactivity ({days_inactive or 'unknown'} days)"

            # Record expiration information
            # In a real system, you might have an expiration_date field
            expiration_time = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Notify customer of expiration (in a real system)
            self.logger.info(
                f"Would notify customer {application.customer_id} of application expiration"
            )

            # Provide option to resubmit (in a real system)
            # This would include instructions on how to submit a new application
            self.logger.info(
                f"Would provide resubmission instructions to customer {application.customer_id}"
            )

            # Log expiration activity
            self.logger.info(
                f"AdoptionApplication {application.technical_id} expired. Reason: {expiration_reason}"
            )

            return application

        except Exception as e:
            self.logger.error(
                f"Error processing application expiration {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_expiration_criteria(
        self, application: AdoptionApplication, kwargs: Dict[str, Any]
    ) -> None:
        """
        Validate that expiration criteria are met.

        Args:
            application: The AdoptionApplication entity
            kwargs: Additional parameters for validation

        Raises:
            ValueError: If expiration criteria are not met
        """
        # Check if application has been inactive long enough
        days_inactive = kwargs.get("daysInactive") or kwargs.get("days_inactive")
        if days_inactive is not None and days_inactive < 30:
            raise ValueError(
                "Application must be inactive for at least 30 days to expire"
            )

        # Check if customer has been contacted (placeholder)
        customer_contacted = kwargs.get("customerContacted") or kwargs.get(
            "customer_contacted"
        )
        if not customer_contacted:
            raise ValueError("Customer must be contacted before expiring application")

        # Check if grace period has passed (placeholder)
        grace_period_passed = kwargs.get("gracePeriodPassed") or kwargs.get(
            "grace_period_passed"
        )
        if not grace_period_passed:
            raise ValueError("Grace period must pass before expiring application")

        self.logger.debug(
            f"Expiration criteria validation passed for application {application.technical_id}"
        )
