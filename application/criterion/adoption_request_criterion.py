"""
AdoptionRequestValidationCriterion for Cyoda Client Application

Validates that an AdoptionRequest meets all required business rules before
it can proceed to the approval stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.adoption_request import AdoptionRequest


class AdoptionRequestValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for AdoptionRequest that checks all business rules
    before the request can proceed to approval stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AdoptionRequestValidationCriterion",
            description="Validates AdoptionRequest business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be AdoptionRequest)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating adoption request {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionRequest for type-safe operations
            adoption_request = cast_entity(entity, AdoptionRequest)

            # Validate required fields
            if (
                not adoption_request.applicant_name
                or len(adoption_request.applicant_name.strip()) < 2
                or len(adoption_request.applicant_name) > 100
            ):
                self.logger.warning(
                    f"Request {adoption_request.technical_id} has invalid applicant name"
                )
                return False

            if not adoption_request.applicant_email or "@" not in adoption_request.applicant_email:
                self.logger.warning(
                    f"Request {adoption_request.technical_id} has invalid email"
                )
                return False

            if not adoption_request.applicant_phone:
                self.logger.warning(
                    f"Request {adoption_request.technical_id} has invalid phone"
                )
                return False

            if (
                not adoption_request.reason_for_adoption
                or len(adoption_request.reason_for_adoption) > 500
            ):
                self.logger.warning(
                    f"Request {adoption_request.technical_id} has invalid reason"
                )
                return False

            if adoption_request.family_size < 1:
                self.logger.warning(
                    f"Request {adoption_request.technical_id} has invalid family size"
                )
                return False

            if (
                not adoption_request.living_situation
                or len(adoption_request.living_situation) > 500
            ):
                self.logger.warning(
                    f"Request {adoption_request.technical_id} has invalid living situation"
                )
                return False

            # Validate experience level
            allowed_levels = ["BEGINNER", "INTERMEDIATE", "ADVANCED"]
            if adoption_request.experience_level not in allowed_levels:
                self.logger.warning(
                    f"Request {adoption_request.technical_id} has invalid experience level"
                )
                return False

            self.logger.info(
                f"Adoption request {adoption_request.technical_id} passed validation"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error validating adoption request: {str(e)}")
            return False

