"""
PetMedicalClearanceProcessor for Purrfect Pets API

Clears pet from medical hold after treatment.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetMedicalClearanceProcessor(CyodaProcessor):
    """
    Processor for Pet medical clearance that clears a pet from medical hold after treatment.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetMedicalClearanceProcessor",
            description="Clears pet from medical hold after treatment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet medical clearance according to functional requirements.

        Args:
            entity: The Pet entity to process (must be on medical hold)
            **kwargs: Additional processing parameters (clearance notes, vet approval)

        Returns:
            The processed pet entity in available state
        """
        try:
            self.logger.info(
                f"Processing Pet medical clearance for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get clearance information from kwargs
            clearance_notes = kwargs.get("clearanceNotes") or kwargs.get("clearance_notes")
            vet_approval = kwargs.get("veterinarianApproval") or kwargs.get("veterinarian_approval")
            treatment_complete = kwargs.get("treatmentComplete") or kwargs.get("treatment_complete")

            # Validate pet is currently on medical hold
            if not pet.is_on_medical_hold():
                raise ValueError("Pet must be on medical hold for clearance")

            # Validate veterinarian approval is provided
            if not vet_approval:
                raise ValueError("Veterinarian approval is required for medical clearance")

            # Validate treatment is complete
            if not treatment_complete:
                raise ValueError("Treatment must be completed for medical clearance")

            # Update medical hold record with clearance information
            # Clear the special_needs field or update it with clearance info
            if clearance_notes:
                pet.special_needs = f"CLEARED: {clearance_notes}"
            else:
                pet.special_needs = None

            # Log medical clearance activity
            self.logger.info(
                f"Pet {pet.technical_id} cleared from medical hold. Notes: {clearance_notes or 'No notes'}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet medical clearance {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
