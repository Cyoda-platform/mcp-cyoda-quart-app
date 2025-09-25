"""
PetAdoptionProcessor for Purrfect Pets API

Handles the final adoption process for pets, including creating adoption records,
updating pet status, and managing adoption data.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetAdoptionProcessor(CyodaProcessor):
    """
    Processor for handling final pet adoptions in the adoption workflow.
    Creates adoption records and updates pet status to adopted.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAdoptionProcessor",
            description="Processes final pet adoptions and updates adoption status",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the pet adoption.

        Args:
            entity: The Pet entity to process (must be in 'reserved' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed pet with adoption data
        """
        try:
            self.logger.info(
                f"Processing pet adoption for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Create adoption data
            adoption_data = self._create_adoption_data(pet)
            pet.adoption_data = adoption_data

            # Update adoption status
            pet.adoption_status = "Adopted"
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} adopted successfully with adoption ID {adoption_data['adoption_id']}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet adoption for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_adoption_data(self, pet: Pet) -> Dict[str, Any]:
        """
        Create adoption data for the pet.

        Args:
            pet: The Pet entity being adopted

        Returns:
            Dictionary containing adoption information
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        adoption_id = str(uuid.uuid4())

        # Calculate follow-up date (30 days from now)
        followup_date = datetime.now(timezone.utc)
        followup_date = followup_date.replace(day=followup_date.day + 30)
        followup_timestamp = followup_date.isoformat().replace("+00:00", "Z")

        adoption_data: Dict[str, Any] = {
            "adoption_id": adoption_id,
            "adopted_at": current_timestamp,
            "followup_date": followup_timestamp,
            "status": "COMPLETED",
            "pet_id": pet.technical_id or pet.entity_id,
            "pet_name": pet.name,
            "adoption_fee": float(pet.price),
            "microchip_required": pet.species in ["Dog", "Cat"],
            "vaccination_status": pet.vaccination_status,
            "health_status": pet.health_status,
            "special_instructions": self._generate_care_instructions(pet),
            "notes": f"Adoption completed for {pet.name} ({pet.species}, {pet.breed})",
        }

        # Include reservation data if available
        if pet.reservation_data:
            adoption_data["reservation_id"] = pet.reservation_data.get("reservation_id")
            adoption_data["reservation_fee_paid"] = pet.reservation_data.get(
                "reservation_fee", 0
            )

        return adoption_data

    def _generate_care_instructions(self, pet: Pet) -> str:
        """
        Generate care instructions based on pet characteristics.

        Args:
            pet: The Pet entity

        Returns:
            Care instructions string
        """
        instructions = []

        # Age-based instructions
        if pet.age_months < 6:
            instructions.append("Young pet - requires frequent feeding and monitoring")
        elif pet.age_months > 84:  # 7+ years
            instructions.append(
                "Senior pet - may need special diet and regular vet checkups"
            )

        # Species-specific instructions
        if pet.species == "Dog":
            instructions.append("Requires daily exercise and socialization")
        elif pet.species == "Cat":
            instructions.append("Provide scratching posts and interactive toys")
        elif pet.species == "Bird":
            instructions.append("Needs spacious cage and social interaction")

        # Health-based instructions
        if pet.special_needs:
            instructions.append(f"Special needs: {pet.special_needs}")

        if pet.vaccination_status != "Up to Date":
            instructions.append("Schedule vaccination update with veterinarian")

        return "; ".join(instructions) if instructions else "Standard pet care applies"

    def _calculate_adoption_success_score(self, pet: Pet) -> float:
        """
        Calculate adoption success score based on pet characteristics.

        Args:
            pet: The Pet entity

        Returns:
            Success score between 0.0 and 1.0
        """
        score = 0.8  # Base score

        # Age factor
        if pet.age_months < 12:
            score += 0.1  # Young pets have higher success
        elif pet.age_months > 84:
            score -= 0.1  # Senior pets may need more care

        # Health factor
        if pet.health_status == "Healthy":
            score += 0.1
        elif pet.health_status in ["Needs Care", "Under Treatment"]:
            score -= 0.1

        # Special needs factor
        if pet.special_needs:
            score -= 0.05

        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
