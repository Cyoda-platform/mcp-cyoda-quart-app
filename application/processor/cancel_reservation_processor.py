"""
CancelReservationProcessor for Pet entities in Purrfect Pets Application

Handles cancellation of pet reservations.
Returns pets to available status when adoption is cancelled.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class CancelReservationProcessor(CyodaProcessor):
    """
    Processor for cancelling Pet reservations.
    Returns pets to available status when adoption process is cancelled.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CancelReservationProcessor",
            description="Cancel pet reservation and return to available status",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Cancel the Pet reservation according to functional requirements.

        Args:
            entity: The Pet entity to cancel reservation for
            **kwargs: Additional processing parameters

        Returns:
            The pet entity returned to available status
        """
        try:
            self.logger.info(
                f"Cancelling reservation for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet reservation can be cancelled
            self._validate_pet_for_cancellation(pet)

            # Cancel the reservation
            self._cancel_pet_reservation(pet)

            self.logger.info(
                f"Pet {pet.technical_id} reservation cancelled successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error cancelling reservation for pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_pet_for_cancellation(self, pet: Pet) -> None:
        """
        Validate that pet reservation can be cancelled.

        Args:
            pet: The Pet entity to validate

        Raises:
            ValueError: If reservation cannot be cancelled
        """
        if not pet.is_reserved():
            raise ValueError(f"Pet {pet.name} is not reserved (current state: {pet.state})")

        self.logger.info(f"Pet {pet.name} validation passed for reservation cancellation")

    def _cancel_pet_reservation(self, pet: Pet) -> None:
        """
        Cancel the pet reservation according to functional requirements.

        Args:
            pet: The Pet entity to cancel reservation for
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Update status back to available
        pet.add_metadata("status", "available")
        pet.add_metadata("reservation_cancelled_date", current_timestamp)
        pet.add_metadata("cancelled_by", "CancelReservationProcessor")

        # Clear reservation-related metadata
        if pet.metadata:
            # Remove reservation-specific metadata
            metadata_to_remove = [
                "reserved_date", 
                "reservation_expires"
            ]
            for key in metadata_to_remove:
                if key in pet.metadata:
                    del pet.metadata[key]

        # Clear adoption references
        pet.clear_adoption_references()

        self.logger.info(
            f"Pet {pet.name} reservation cancelled and returned to available status on {current_timestamp}"
        )
