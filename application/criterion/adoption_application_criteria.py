"""
AdoptionApplication Criteria for Purrfect Pets API

Validation criteria for adoption application business rules and workflows.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.adoptionapplication.version_1.adoptionapplication import AdoptionApplication


class ApplicationCompletenessCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for checking adoption application completeness.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationCompletenessCriterion",
            description="Validates adoption application completeness",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if adoption application is complete.

        Args:
            entity: The AdoptionApplication entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if application is complete, False otherwise
        """
        try:
            self.logger.info(
                f"Validating application completeness {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionApplication for type-safe operations
            application = cast_entity(entity, AdoptionApplication)

            # Validate required fields
            if not self._validate_required_fields(application):
                return False

            # Validate field lengths and content quality
            if not self._validate_field_quality(application):
                return False

            # Validate terms agreement
            if not application.agreed_to_terms:
                self.logger.warning(
                    f"Application {application.technical_id} - terms not agreed to"
                )
                return False

            # Validate application fee
            if application.application_fee <= 0:
                self.logger.warning(
                    f"Application {application.technical_id} - invalid application fee: {application.application_fee}"
                )
                return False

            self.logger.info(
                f"Application {application.technical_id} passed completeness validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating application completeness {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, application: AdoptionApplication) -> bool:
        """Validate required fields are present."""
        required_fields = [
            ("customer_id", application.customer_id),
            ("pet_id", application.pet_id),
            ("reason_for_adoption", application.reason_for_adoption),
            ("living_arrangement", application.living_arrangement),
            ("work_schedule", application.work_schedule),
            ("pet_care_experience", application.pet_care_experience),
            ("veterinarian_contact", application.veterinarian_contact),
            ("references", application.references),
        ]

        for field_name, field_value in required_fields:
            if not field_value or (isinstance(field_value, str) and len(field_value.strip()) == 0):
                self.logger.warning(
                    f"Application {application.technical_id} - missing required field: {field_name}"
                )
                return False

        return True

    def _validate_field_quality(self, application: AdoptionApplication) -> bool:
        """Validate field content quality."""
        # Check minimum lengths for text fields
        text_fields = [
            ("reason_for_adoption", application.reason_for_adoption, 10),
            ("living_arrangement", application.living_arrangement, 10),
            ("work_schedule", application.work_schedule, 5),
            ("pet_care_experience", application.pet_care_experience, 10),
            ("veterinarian_contact", application.veterinarian_contact, 10),
            ("references", application.references, 10),
        ]

        for field_name, field_value, min_length in text_fields:
            if len(field_value.strip()) < min_length:
                self.logger.warning(
                    f"Application {application.technical_id} - {field_name} too short: {len(field_value)} < {min_length}"
                )
                return False

        return True


class ApplicationApprovalCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for checking if adoption application can be approved.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationApprovalCriterion",
            description="Validates adoption application for approval",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if adoption application can be approved.

        Args:
            entity: The AdoptionApplication entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if application can be approved, False otherwise
        """
        try:
            self.logger.info(
                f"Validating application approval {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionApplication for type-safe operations
            application = cast_entity(entity, AdoptionApplication)

            # Application must be under review
            if not application.is_under_review():
                self.logger.warning(
                    f"Application {application.technical_id} is not under review: {application.state}"
                )
                return False

            # Must have reviewer assigned
            if not application.reviewer_id:
                self.logger.warning(
                    f"Application {application.technical_id} has no reviewer assigned"
                )
                return False

            # Validate application content quality
            if not self._validate_application_quality(application):
                return False

            # Check for any red flags in the application
            if not self._check_red_flags(application):
                return False

            # Validate references (simulated)
            if not self._validate_references(application):
                return False

            # Validate veterinarian contact (simulated)
            if not self._validate_veterinarian_contact(application):
                return False

            self.logger.info(
                f"Application {application.technical_id} passed approval validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating application approval {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_application_quality(self, application: AdoptionApplication) -> bool:
        """Validate application content quality."""
        # Check for thoughtful responses
        if "just because" in application.reason_for_adoption.lower():
            self.logger.warning(
                f"Application {application.technical_id} - insufficient reason for adoption"
            )
            return False

        # Check work schedule compatibility
        if "24/7" in application.work_schedule.lower() or "always working" in application.work_schedule.lower():
            self.logger.warning(
                f"Application {application.technical_id} - work schedule may not be compatible with pet care"
            )
            return False

        return True

    def _check_red_flags(self, application: AdoptionApplication) -> bool:
        """Check for red flags in the application."""
        red_flag_phrases = [
            "breeding", "resell", "profit", "fighting", "guard dog only",
            "outdoor only", "chain", "no vet", "can't afford vet"
        ]

        all_text = f"{application.reason_for_adoption} {application.living_arrangement} {application.pet_care_experience}".lower()

        for phrase in red_flag_phrases:
            if phrase in all_text:
                self.logger.warning(
                    f"Application {application.technical_id} - red flag detected: {phrase}"
                )
                return False

        return True

    def _validate_references(self, application: AdoptionApplication) -> bool:
        """Validate references (simulated)."""
        # In a real implementation, this would contact references
        if len(application.references.strip()) < 20:
            self.logger.warning(
                f"Application {application.technical_id} - insufficient reference information"
            )
            return False

        self.logger.info(f"References validated for application {application.technical_id}")
        return True

    def _validate_veterinarian_contact(self, application: AdoptionApplication) -> bool:
        """Validate veterinarian contact (simulated)."""
        # In a real implementation, this would verify the vet contact
        if "no vet" in application.veterinarian_contact.lower() or "none" in application.veterinarian_contact.lower():
            self.logger.warning(
                f"Application {application.technical_id} - no veterinarian contact provided"
            )
            return False

        self.logger.info(f"Veterinarian contact validated for application {application.technical_id}")
        return True
