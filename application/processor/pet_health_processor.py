"""
PetHealthProcessor for Purrfect Pets API

Handles health status updates for pets, including medical records,
treatment tracking, and health clearance processing.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetHealthProcessor(CyodaProcessor):
    """
    Processor for handling pet health status updates and medical care tracking.
    Manages health records and treatment status for pets requiring medical attention.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetHealthProcessor",
            description="Processes pet health status updates and medical care tracking",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the pet health status update.

        Args:
            entity: The Pet entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed pet with updated health information
        """
        try:
            self.logger.info(
                f"Processing pet health update for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Create health record
            health_record = self._create_health_record(pet)

            # Update pet metadata with health record
            if not pet.metadata:
                pet.metadata = {}

            if "health_records" not in pet.metadata:
                pet.metadata["health_records"] = []

            pet.metadata["health_records"].append(health_record)

            # Update health status based on current condition
            pet.health_status = self._determine_health_status(pet)

            # Update adoption status if health affects availability
            if pet.health_status == "Under Treatment":
                pet.adoption_status = "Not Available"
            elif (
                pet.health_status in ["Healthy", "Recovering"]
                and pet.adoption_status == "Not Available"
            ):
                pet.adoption_status = "Available"

            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} health status updated to {pet.health_status}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet health update for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_health_record(self, pet: Pet) -> Dict[str, Any]:
        """
        Create a health record entry for the pet.

        Args:
            pet: The Pet entity

        Returns:
            Dictionary containing health record information
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        record_id = str(uuid.uuid4())

        health_record: Dict[str, Any] = {
            "record_id": record_id,
            "recorded_at": current_timestamp,
            "pet_id": pet.technical_id or pet.entity_id,
            "pet_name": pet.name,
            "health_status": pet.health_status,
            "vaccination_status": pet.vaccination_status,
            "examination_type": self._determine_examination_type(pet),
            "findings": self._generate_health_findings(pet),
            "treatment_plan": self._generate_treatment_plan(pet),
            "next_checkup": self._calculate_next_checkup_date(pet),
            "veterinarian_notes": f"Health assessment for {pet.name}",
        }

        return health_record

    def _determine_health_status(self, pet: Pet) -> str:
        """
        Determine the appropriate health status based on pet condition.

        Args:
            pet: The Pet entity

        Returns:
            Health status string
        """
        # Check existing health records for patterns
        if pet.metadata and "health_records" in pet.metadata:
            recent_records = pet.metadata["health_records"][-3:]  # Last 3 records

            # If multiple recent treatments, might be recovering
            if len(recent_records) >= 2:
                treatment_count = sum(
                    1
                    for record in recent_records
                    if "treatment" in record.get("treatment_plan", "").lower()
                )
                if treatment_count >= 2:
                    return "Recovering"

        # Default logic based on current status
        if pet.health_status == "Under Treatment":
            return "Recovering"  # Assume improvement
        elif pet.health_status == "Needs Care":
            return "Under Treatment"  # Start treatment
        else:
            return "Healthy"  # Maintain or improve status

    def _determine_examination_type(self, pet: Pet) -> str:
        """
        Determine the type of examination needed.

        Args:
            pet: The Pet entity

        Returns:
            Examination type string
        """
        if pet.age_months < 6:
            return "Puppy/Kitten Wellness Check"
        elif pet.age_months > 84:  # 7+ years
            return "Senior Pet Health Assessment"
        elif pet.health_status in ["Needs Care", "Under Treatment"]:
            return "Medical Treatment Follow-up"
        else:
            return "Routine Health Check"

    def _generate_health_findings(self, pet: Pet) -> str:
        """
        Generate health findings based on pet characteristics.

        Args:
            pet: The Pet entity

        Returns:
            Health findings string
        """
        findings = []

        # Age-related findings
        if pet.age_months < 6:
            findings.append("Young animal - monitoring growth and development")
        elif pet.age_months > 84:
            findings.append("Senior animal - checking for age-related conditions")

        # Species-specific findings
        if pet.species == "Dog":
            findings.append("Canine health assessment completed")
        elif pet.species == "Cat":
            findings.append("Feline health assessment completed")

        # Health status findings
        if pet.health_status == "Healthy":
            findings.append("No significant health concerns identified")
        elif pet.health_status == "Needs Care":
            findings.append("Minor health issues requiring attention")
        elif pet.health_status == "Under Treatment":
            findings.append("Ongoing treatment showing positive response")

        # Vaccination findings
        if pet.vaccination_status != "Up to Date":
            findings.append("Vaccination schedule needs updating")

        return (
            "; ".join(findings) if findings else "Standard health assessment completed"
        )

    def _generate_treatment_plan(self, pet: Pet) -> str:
        """
        Generate treatment plan based on pet needs.

        Args:
            pet: The Pet entity

        Returns:
            Treatment plan string
        """
        treatments = []

        # Vaccination plan
        if pet.vaccination_status in ["Needs Update", "Not Vaccinated", "Partial"]:
            treatments.append("Update vaccination schedule")

        # Age-specific treatments
        if pet.age_months < 6:
            treatments.append("Continue puppy/kitten care protocol")
        elif pet.age_months > 84:
            treatments.append("Senior pet monitoring and care")

        # Health-specific treatments
        if pet.health_status == "Needs Care":
            treatments.append("Begin appropriate medical treatment")
        elif pet.health_status == "Under Treatment":
            treatments.append("Continue current treatment protocol")

        # Special needs treatments
        if pet.special_needs:
            treatments.append(f"Address special needs: {pet.special_needs}")

        return "; ".join(treatments) if treatments else "Maintain current care routine"

    def _calculate_next_checkup_date(self, pet: Pet) -> str:
        """
        Calculate the next checkup date based on pet needs.

        Args:
            pet: The Pet entity

        Returns:
            Next checkup date as ISO string
        """
        current_date = datetime.now(timezone.utc)

        # Determine checkup interval based on health status and age
        if pet.health_status == "Under Treatment":
            days_ahead = 7  # Weekly checkups during treatment
        elif pet.age_months < 6:
            days_ahead = 14  # Bi-weekly for young pets
        elif pet.age_months > 84:
            days_ahead = 30  # Monthly for senior pets
        else:
            days_ahead = 90  # Quarterly for healthy adults

        next_checkup = current_date.replace(day=current_date.day + days_ahead)
        return next_checkup.isoformat().replace("+00:00", "Z")
