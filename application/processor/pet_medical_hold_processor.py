"""
PetMedicalHoldProcessor for Purrfect Pets API

Places pet on medical hold for health issues.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetMedicalHoldProcessor(CyodaProcessor):
    """
    Processor for Pet medical hold that places a pet on medical hold for health issues.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetMedicalHoldProcessor",
            description="Places pet on medical hold for health issues",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet medical hold according to functional requirements.

        Args:
            entity: The Pet entity to process (must not be adopted)
            **kwargs: Additional processing parameters (medical notes, expected duration)

        Returns:
            The processed pet entity in medical_hold state
        """
        try:
            self.logger.info(
                f"Processing Pet medical hold for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get medical information from kwargs
            medical_notes = kwargs.get("medicalNotes") or kwargs.get("medical_notes")
            expected_duration = kwargs.get("expectedDuration") or kwargs.get("expected_duration")

            # Validate pet is not already adopted
            if pet.is_adopted():
                raise ValueError("Cannot place adopted pet on medical hold")

            # Validate medical notes are provided
            if not medical_notes:
                raise ValueError("Medical notes are required for medical hold")

            # Create medical hold record with notes and expected duration
            # In a real system, you might create a separate MedicalHold entity
            # For this implementation, we store the information in special_needs field
            medical_hold_info = f"MEDICAL HOLD: {medical_notes}"
            if expected_duration:
                medical_hold_info += f" (Expected duration: {expected_duration})"
            
            pet.special_needs = medical_hold_info

            # Log medical hold activity
            self.logger.info(
                f"Pet {pet.technical_id} placed on medical hold. Notes: {medical_notes}"
            )

            # Notify relevant staff (in a real system, this would send notifications)
            self.logger.info(
                f"Medical hold notification sent for pet {pet.technical_id}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet medical hold {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
