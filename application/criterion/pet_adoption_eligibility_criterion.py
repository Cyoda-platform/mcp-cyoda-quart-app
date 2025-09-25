"""
PetAdoptionEligibilityCriterion for Purrfect Pets API

Validates that a pet meets all required criteria for adoption eligibility
before it can be reserved by potential adopters.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.pet.version_1.pet import Pet


class PetAdoptionEligibilityCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Pet adoption eligibility that checks all business rules
    before the pet can be reserved for adoption.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAdoptionEligibilityCriterion",
            description="Validates pet adoption eligibility and readiness for reservation",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet meets all adoption eligibility criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if the pet meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating adoption eligibility for pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check basic adoption status
            if pet.adoption_status != "Available":
                self.logger.warning(
                    f"Pet {pet.technical_id} is not available for adoption (status: {pet.adoption_status})"
                )
                return False

            # Check health status eligibility
            if not self._check_health_eligibility(pet):
                return False

            # Check age eligibility
            if not self._check_age_eligibility(pet):
                return False

            # Check vaccination requirements
            if not self._check_vaccination_eligibility(pet):
                return False

            # Check special requirements
            if not self._check_special_requirements(pet):
                return False

            self.logger.info(
                f"Pet {pet.technical_id} passed all adoption eligibility criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating adoption eligibility for pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _check_health_eligibility(self, pet: Pet) -> bool:
        """
        Check if pet's health status allows for adoption.

        Args:
            pet: The Pet entity

        Returns:
            True if health status is acceptable for adoption
        """
        eligible_health_statuses = ["Healthy", "Recovering"]

        if pet.health_status not in eligible_health_statuses:
            self.logger.warning(
                f"Pet {pet.technical_id} health status '{pet.health_status}' not eligible for adoption"
            )
            return False

        # Pets under treatment should not be adopted
        if pet.health_status == "Under Treatment":
            self.logger.warning(
                f"Pet {pet.technical_id} is currently under treatment and not available for adoption"
            )
            return False

        return True

    def _check_age_eligibility(self, pet: Pet) -> bool:
        """
        Check if pet's age meets adoption requirements.

        Args:
            pet: The Pet entity

        Returns:
            True if age is appropriate for adoption
        """
        # Very young pets (under 8 weeks) need special handling
        if pet.age_months < 2:
            # Allow adoption only if special care arrangements are noted
            if not pet.special_needs or "special care" not in pet.special_needs.lower():
                self.logger.warning(
                    f"Pet {pet.technical_id} is too young ({pet.age_months} months) for standard adoption"
                )
                return False

        # No upper age limit, but log for very old pets
        if pet.age_months > 180:  # 15+ years
            self.logger.info(
                f"Pet {pet.technical_id} is a senior pet ({pet.get_age_display()}) - special care may be needed"
            )

        return True

    def _check_vaccination_eligibility(self, pet: Pet) -> bool:
        """
        Check if pet's vaccination status meets adoption requirements.

        Args:
            pet: The Pet entity

        Returns:
            True if vaccination status is acceptable
        """
        # For dogs and cats, vaccinations are more critical
        if pet.species in ["Dog", "Cat"]:
            if pet.vaccination_status == "Not Vaccinated":
                self.logger.warning(
                    f"Pet {pet.technical_id} ({pet.species}) requires vaccination before adoption"
                )
                return False

        # Partial vaccinations are acceptable with follow-up plan
        if pet.vaccination_status == "Partial":
            self.logger.info(
                f"Pet {pet.technical_id} has partial vaccinations - adopter will need to complete schedule"
            )

        return True

    def _check_special_requirements(self, pet: Pet) -> bool:
        """
        Check special requirements and restrictions.

        Args:
            pet: The Pet entity

        Returns:
            True if special requirements don't prevent adoption
        """
        # Check for any adoption-blocking special needs
        if pet.special_needs:
            blocking_conditions = [
                "quarantine",
                "aggressive behavior",
                "severe medical condition",
                "not suitable for adoption",
            ]

            special_needs_lower = pet.special_needs.lower()
            for condition in blocking_conditions:
                if condition in special_needs_lower:
                    self.logger.warning(
                        f"Pet {pet.technical_id} has adoption-blocking condition: {pet.special_needs}"
                    )
                    return False

        # Check price reasonableness
        if pet.price <= 0:
            self.logger.warning(
                f"Pet {pet.technical_id} has invalid adoption fee: ${pet.price}"
            )
            return False

        # Very high prices might indicate special circumstances
        if pet.price > 5000:
            self.logger.info(
                f"Pet {pet.technical_id} has high adoption fee (${pet.price}) - may require special approval"
            )

        return True

    def _check_documentation_completeness(self, pet: Pet) -> bool:
        """
        Check if pet has complete documentation for adoption.

        Args:
            pet: The Pet entity

        Returns:
            True if documentation is complete
        """
        # Check required fields
        required_fields = [pet.name, pet.species, pet.breed, pet.description]

        for field in required_fields:
            if not field or (isinstance(field, str) and len(field.strip()) == 0):
                self.logger.warning(
                    f"Pet {pet.technical_id} missing required documentation"
                )
                return False

        # Check description quality
        if len(pet.description) < 20:
            self.logger.warning(
                f"Pet {pet.technical_id} description too brief for adoption listing"
            )
            return False

        return True
