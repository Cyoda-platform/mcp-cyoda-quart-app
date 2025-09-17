"""
ApplicationApprovalCriterion for Purrfect Pets API

Checks if an adoption application can be approved.
"""

from typing import Any

from application.entity.adoption_application.version_1.adoption_application import (
    AdoptionApplication,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ApplicationApprovalCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if an adoption application can be approved.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationApprovalCriterion",
            description="Checks if an adoption application can be approved",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the adoption application can be approved.

        Args:
            entity: The AdoptionApplication entity to check
            **kwargs: Additional criteria parameters (review data)

        Returns:
            True if the application can be approved, False otherwise
        """
        try:
            self.logger.info(
                f"Checking application approval eligibility for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionApplication for type-safe operations
            application = cast_entity(entity, AdoptionApplication)

            # Check if application's current state is UNDER_REVIEW
            if not application.is_under_review():
                self.logger.info(
                    f"Application {application.technical_id} is not under review (current state: {application.state})"
                )
                return False

            # Get review data from kwargs
            background_check_passed = kwargs.get("backgroundCheckPassed") or kwargs.get(
                "background_check_passed"
            )
            references_verified = kwargs.get("referencesVerified") or kwargs.get(
                "references_verified"
            )
            housing_approved = kwargs.get("housingApproved") or kwargs.get(
                "housing_approved"
            )
            customer_blacklisted = kwargs.get("customerBlacklisted") or kwargs.get(
                "customer_blacklisted"
            )
            pet_compatibility_confirmed = kwargs.get(
                "petCompatibilityConfirmed"
            ) or kwargs.get("pet_compatibility_confirmed")

            # Check if background check passed
            if not background_check_passed:
                self.logger.info(
                    f"Application {application.technical_id} background check did not pass"
                )
                return False

            # Check if references are verified
            if not references_verified:
                self.logger.info(
                    f"Application {application.technical_id} references not verified"
                )
                return False

            # Check if housing situation is approved
            if not housing_approved:
                self.logger.info(
                    f"Application {application.technical_id} housing situation not approved"
                )
                return False

            # Check if customer is blacklisted
            if customer_blacklisted:
                self.logger.info(
                    f"Application {application.technical_id} customer is blacklisted"
                )
                return False

            # Check if pet compatibility is confirmed
            if not pet_compatibility_confirmed:
                self.logger.info(
                    f"Application {application.technical_id} pet compatibility not confirmed"
                )
                return False

            self.logger.info(f"Application {application.technical_id} can be approved")
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking application approval eligibility for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
