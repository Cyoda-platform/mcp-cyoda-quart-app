"""
PetAvailableProcessor for Purrfect Pets API

Handles marking pets as available again after being unavailable.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetAvailableProcessor(CyodaProcessor):
    """
    Processor for marking pets as available again.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAvailableProcessor",
            description="Processes pets being marked as available again",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process marking the Pet as available again.

        Args:
            entity: The Pet entity to mark as available
            **kwargs: Additional processing parameters

        Returns:
            The processed pet entity marked as available
        """
        try:
            self.logger.info(
                f"Processing Pet available {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # 1. Clear unavailability flags
            if pet.metadata:
                pet.metadata.pop("unavailability_reason", None)
                pet.metadata.pop("unavailable_date", None)
                pet.metadata.pop("temporarily_unavailable", None)

            # 2. Validate pet readiness for adoption (simulated)
            await self._validate_pet_readiness(pet)

            # 3. Notify adoption staff of availability (simulated)
            await self._notify_adoption_staff_availability(pet)

            # 4. Update listing visibility (simulated)
            await self._update_listing_visibility(pet)

            # 5. Record availability restoration
            pet.add_metadata(
                "availability_restored_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )

            # 6. Update pet state to AVAILABLE (handled by workflow transition)
            self.logger.info(f"Pet available {pet.technical_id} processed successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet available {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_pet_readiness(self, pet: Pet) -> None:
        """
        Validate pet readiness for adoption (simulated).

        Args:
            pet: The pet entity
        """
        # In a real implementation, this would check health status, vaccinations, etc.
        self.logger.info(f"Pet readiness validated for {pet.technical_id}")

    async def _notify_adoption_staff_availability(self, pet: Pet) -> None:
        """
        Notify adoption staff of availability (simulated).

        Args:
            pet: The pet entity
        """
        # In a real implementation, this would send notifications to staff
        self.logger.info(
            f"Adoption staff notified that pet {pet.name} ({pet.technical_id}) is now available"
        )

    async def _update_listing_visibility(self, pet: Pet) -> None:
        """
        Update listing visibility (simulated).

        Args:
            pet: The pet entity
        """
        # In a real implementation, this would update website listings, etc.
        self.logger.info(
            f"Listing visibility updated for pet {pet.name} ({pet.technical_id})"
        )
