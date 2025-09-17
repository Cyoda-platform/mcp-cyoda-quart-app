"""
PetReservationCancellationProcessor for Purrfect Pets API

Cancels a pet reservation and makes pet available again.
"""

import logging
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetReservationCancellationProcessor(CyodaProcessor):
    """
    Processor for Pet reservation cancellation that cancels a pet reservation
    and makes the pet available again.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationCancellationProcessor",
            description="Cancels a pet reservation and makes pet available again",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet reservation cancellation according to functional requirements.

        Args:
            entity: The Pet entity to process (must be in reserved state)
            **kwargs: Additional processing parameters (cancellation reason)

        Returns:
            The processed pet entity in available state
        """
        try:
            self.logger.info(
                f"Processing Pet reservation cancellation for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get cancellation reason from kwargs
            cancellation_reason = kwargs.get("cancellationReason") or kwargs.get(
                "cancellation_reason"
            )

            # Validate pet is currently reserved
            if not pet.is_reserved():
                raise ValueError("Pet must be reserved to cancel reservation")

            # Remove reservation record (in a real system, you might have a separate Reservation entity)
            # For this implementation, we just log the cancellation

            # Clear reservation-related fields (if any were stored on the pet)
            # In this simple implementation, the state transition handles this

            # Log cancellation with reason
            reason_text = cancellation_reason or "No reason provided"
            self.logger.info(
                f"Pet {pet.technical_id} reservation cancelled. Reason: {reason_text}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet reservation cancellation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
