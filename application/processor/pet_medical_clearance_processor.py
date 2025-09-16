"""
PetMedicalClearanceProcessor for Purrfect Pets API

Handles clearing pets from medical hold when they are healthy again.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetMedicalClearanceProcessor(CyodaProcessor):
    """
    Processor for clearing pets from medical hold.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetMedicalClearanceProcessor",
            description="Processes pets being cleared from medical hold",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process clearing the Pet from medical hold.

        Args:
            entity: The Pet entity to clear from medical hold
            **kwargs: Additional processing parameters

        Returns:
            The processed pet entity cleared from medical hold
        """
        try:
            self.logger.info(
                f"Processing Pet medical clearance {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # 1. Validate medical clearance documentation (simulated)
            clearance_data = kwargs.get("clearance_data", {})
            await self._validate_medical_clearance(pet, clearance_data)

            # 2. Update health records
            pet.add_metadata(
                "medical_clearance_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )
            pet.add_metadata(
                "cleared_by", clearance_data.get("veterinarian", "Medical Staff")
            )

            # 3. Clear medical hold flags
            if pet.metadata:
                pet.metadata.pop("medical_hold_reason", None)
                pet.metadata.pop("medical_hold_date", None)

            # 4. Notify adoption staff of availability (simulated)
            await self._notify_adoption_staff_availability(pet)

            # 5. Update vaccination status if applicable
            if clearance_data.get("vaccinations_updated"):
                pet.vaccinated = True
                pet.add_metadata(
                    "last_vaccination_date",
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                )

            # 6. Update pet state to AVAILABLE (handled by workflow transition)
            self.logger.info(
                f"Pet medical clearance {pet.technical_id} processed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet medical clearance {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_medical_clearance(self, pet: Pet, clearance_data: Dict[str, Any]) -> None:
        """
        Validate medical clearance documentation (simulated).

        Args:
            pet: The pet entity
            clearance_data: Medical clearance data
        """
        # In a real implementation, this would validate medical documents
        required_fields = ["veterinarian", "clearance_notes"]
        for field in required_fields:
            if field not in clearance_data:
                self.logger.warning(f"Missing clearance field: {field}")

        self.logger.info(f"Medical clearance validated for pet {pet.technical_id}")

    async def _notify_adoption_staff_availability(self, pet: Pet) -> None:
        """
        Notify adoption staff of pet availability (simulated).

        Args:
            pet: The pet entity
        """
        # In a real implementation, this would send notifications to staff
        self.logger.info(
            f"Adoption staff notified that pet {pet.name} ({pet.technical_id}) is now available"
        )
