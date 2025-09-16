"""
PetUnavailableProcessor for Purrfect Pets API

Handles marking pets as unavailable for various reasons.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetUnavailableProcessor(CyodaProcessor):
    """
    Processor for marking pets as unavailable.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetUnavailableProcessor",
            description="Processes pets being marked as unavailable",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process marking the Pet as unavailable.

        Args:
            entity: The Pet entity to mark as unavailable
            **kwargs: Additional processing parameters (should include unavailability_reason)

        Returns:
            The processed pet entity marked as unavailable
        """
        try:
            self.logger.info(
                f"Processing Pet unavailable {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get unavailability reason from kwargs
            unavailability_reason = kwargs.get(
                "unavailability_reason", "Temporarily unavailable"
            )

            # 1. Record unavailability reason
            pet.add_metadata("unavailability_reason", unavailability_reason)
            pet.add_metadata(
                "unavailable_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )

            # 2. Cancel any existing reservations
            if pet.adopter_id:
                await self._cancel_existing_reservation(pet, unavailability_reason)

            # 3. Notify interested customers (simulated)
            await self._notify_interested_customers(pet, unavailability_reason)

            # 4. Set temporary unavailability flag
            pet.add_metadata("temporarily_unavailable", True)

            # 5. Update pet state to UNAVAILABLE (handled by workflow transition)
            self.logger.info(
                f"Pet unavailable {pet.technical_id} processed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet unavailable {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _cancel_existing_reservation(self, pet: Pet, reason: str) -> None:
        """
        Cancel any existing reservations.

        Args:
            pet: The pet entity
            reason: Reason for unavailability
        """
        customer_id = pet.adopter_id
        pet.adopter_id = None

        if pet.metadata and "reservation_timestamp" in pet.metadata:
            del pet.metadata["reservation_timestamp"]

        # Notify customer of cancellation
        if customer_id:
            self.logger.info(
                f"Reservation cancelled for customer {customer_id} - Pet {pet.technical_id} unavailable: {reason}"
            )

    async def _notify_interested_customers(self, pet: Pet, reason: str) -> None:
        """
        Notify interested customers (simulated).

        Args:
            pet: The pet entity
            reason: Reason for unavailability
        """
        # In a real implementation, this would notify customers who showed interest
        self.logger.info(
            f"Interested customers notified that pet {pet.name} ({pet.technical_id}) is unavailable: {reason}"
        )
