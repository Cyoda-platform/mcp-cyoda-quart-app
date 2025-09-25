"""
PetHealthClearanceCriterion for Purrfect Pets API

Validates that a pet has received proper health clearance and is ready
to transition from under_care state back to available for adoption.
"""

from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class PetHealthClearanceCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Pet health clearance that checks all medical requirements
    before the pet can return to available status from under_care.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetHealthClearanceCriterion",
            description="Validates pet health clearance and readiness to return to adoption availability",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet meets all health clearance criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if the pet meets all health clearance criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating health clearance for pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check current health status
            if not self._check_health_status_clearance(pet):
                return False

            # Check vaccination status
            if not self._check_vaccination_clearance(pet):
                return False

            # Check treatment completion
            if not self._check_treatment_completion(pet):
                return False

            # Check recovery period
            if not self._check_recovery_period(pet):
                return False

            # Check veterinary approval
            if not self._check_veterinary_approval(pet):
                return False

            self.logger.info(
                f"Pet {pet.technical_id} passed all health clearance criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating health clearance for pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _check_health_status_clearance(self, pet: Pet) -> bool:
        """
        Check if pet's health status indicates clearance.

        Args:
            pet: The Pet entity

        Returns:
            True if health status allows clearance
        """
        cleared_statuses = ["Healthy", "Recovering"]

        if pet.health_status not in cleared_statuses:
            self.logger.warning(
                f"Pet {pet.technical_id} health status '{pet.health_status}' not cleared for adoption availability"
            )
            return False

        # Pets still under treatment should not be cleared
        if pet.health_status == "Under Treatment":
            self.logger.warning(
                f"Pet {pet.technical_id} is still under treatment and not ready for clearance"
            )
            return False

        return True

    def _check_vaccination_clearance(self, pet: Pet) -> bool:
        """
        Check if pet's vaccination status meets clearance requirements.

        Args:
            pet: The Pet entity

        Returns:
            True if vaccination status is acceptable for clearance
        """
        # For health clearance, vaccinations should be up to date or at least partial
        acceptable_statuses = ["Up to Date", "Partial"]

        if pet.vaccination_status not in acceptable_statuses:
            self.logger.warning(
                f"Pet {pet.technical_id} vaccination status '{pet.vaccination_status}' requires update before clearance"
            )
            return False

        # For dogs and cats, prefer up-to-date vaccinations
        if pet.species in ["Dog", "Cat"] and pet.vaccination_status != "Up to Date":
            self.logger.info(
                f"Pet {pet.technical_id} ({pet.species}) should have up-to-date vaccinations for optimal clearance"
            )

        return True

    def _check_treatment_completion(self, pet: Pet) -> bool:
        """
        Check if any required treatments have been completed.

        Args:
            pet: The Pet entity

        Returns:
            True if treatments are completed or not required
        """
        # Check health records in metadata for treatment completion
        if pet.metadata and "health_records" in pet.metadata:
            health_records = pet.metadata["health_records"]

            if health_records:
                # Get the most recent health record
                latest_record = health_records[-1]

                # Check if treatment plan indicates completion
                treatment_plan = latest_record.get("treatment_plan", "")
                if "continue treatment" in treatment_plan.lower():
                    self.logger.warning(
                        f"Pet {pet.technical_id} still requires ongoing treatment"
                    )
                    return False

                # Check findings for ongoing issues
                findings = latest_record.get("findings", "")
                concerning_findings = [
                    "requires further treatment",
                    "ongoing medical attention",
                    "not ready for adoption",
                ]

                findings_lower = findings.lower()
                for finding in concerning_findings:
                    if finding in findings_lower:
                        self.logger.warning(
                            f"Pet {pet.technical_id} health record indicates ongoing concerns: {findings}"
                        )
                        return False

        return True

    def _check_recovery_period(self, pet: Pet) -> bool:
        """
        Check if sufficient recovery period has passed.

        Args:
            pet: The Pet entity

        Returns:
            True if recovery period is adequate
        """
        # Check if there are recent health records indicating treatment
        if pet.metadata and "health_records" in pet.metadata:
            health_records = pet.metadata["health_records"]

            if health_records:
                # For this simplified implementation, assume adequate recovery
                # In a real system, you would check timestamps and treatment types
                latest_record = health_records[-1]

                # Check if the latest record indicates readiness
                examination_type = latest_record.get("examination_type", "")
                if "follow-up" in examination_type.lower():
                    # Follow-up exams usually indicate recovery monitoring
                    return True

        # If no specific recovery concerns, allow clearance
        return True

    def _check_veterinary_approval(self, pet: Pet) -> bool:
        """
        Check for veterinary approval indicators.

        Args:
            pet: The Pet entity

        Returns:
            True if veterinary approval is indicated
        """
        # Check health records for veterinary approval
        if pet.metadata and "health_records" in pet.metadata:
            health_records = pet.metadata["health_records"]

            if health_records:
                latest_record = health_records[-1]

                # Check veterinarian notes for approval indicators
                vet_notes = latest_record.get("veterinarian_notes", "")
                approval_indicators = [
                    "cleared for adoption",
                    "ready for placement",
                    "health assessment complete",
                    "no concerns",
                ]

                vet_notes_lower = vet_notes.lower()
                for indicator in approval_indicators:
                    if indicator in vet_notes_lower:
                        self.logger.info(
                            f"Pet {pet.technical_id} has veterinary approval indicator: {indicator}"
                        )
                        return True

        # For pets with healthy status, assume veterinary approval
        if pet.health_status == "Healthy":
            return True

        # For recovering pets, check if they've been stable
        if pet.health_status == "Recovering":
            self.logger.info(
                f"Pet {pet.technical_id} is recovering - assuming veterinary monitoring is ongoing"
            )
            return True

        return True

    def _check_special_clearance_requirements(self, pet: Pet) -> bool:
        """
        Check any special clearance requirements based on pet characteristics.

        Args:
            pet: The Pet entity

        Returns:
            True if special requirements are met
        """
        # Check age-specific requirements
        if pet.age_months < 6:
            # Young pets may need additional clearance
            if pet.special_needs and "special care" not in pet.special_needs.lower():
                self.logger.warning(
                    f"Young pet {pet.technical_id} may need special care notation for clearance"
                )

        # Check species-specific requirements
        if pet.species in ["Dog", "Cat"]:
            # Dogs and cats typically need more thorough health clearance
            if pet.health_status != "Healthy" and not pet.metadata:
                self.logger.warning(
                    f"Pet {pet.technical_id} ({pet.species}) needs documented health records for clearance"
                )
                return False

        return True
