"""
PetReservationCancelProcessor for Purrfect Pets API

Handles the cancellation of pet reservations, clearing adopter information
and making the pet available again.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetReservationCancelProcessor(CyodaProcessor):
    """
    Processor for Pet reservation cancellation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationCancelProcessor",
            description="Processes pet reservation cancellations",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet reservation cancellation according to functional requirements.

        Args:
            entity: The Pet entity to cancel reservation for
            **kwargs: Additional processing parameters

        Returns:
            The processed pet entity with cleared reservation data
        """
        try:
            self.logger.info(
                f"Processing Pet reservation cancellation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Store customer ID for notification before clearing
            customer_id = pet.adopter_id

            # 1. Clear adopter ID
            pet.adopter_id = None

            # 2. Remove reservation timestamp
            if pet.metadata and "reservation_timestamp" in pet.metadata:
                del pet.metadata["reservation_timestamp"]

            # 3. Cancel any scheduled follow-up reminders (simulated)
            if customer_id:
                await self._cancel_reservation_reminders(customer_id, pet)

            # 4. Send cancellation notification to customer (simulated)
            if customer_id:
                await self._send_cancellation_notification(customer_id, pet)

            # 5. Log cancellation reason
            cancellation_reason = kwargs.get(
                "cancellation_reason", "No reason provided"
            )
            pet.add_metadata("last_cancellation_reason", cancellation_reason)
            pet.add_metadata("last_cancellation_date", pet.updated_at or pet.created_at)

            # 6. Update pet state to AVAILABLE (handled by workflow transition)
            self.logger.info(
                f"Pet reservation cancellation {pet.technical_id} processed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet reservation cancellation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _cancel_reservation_reminders(self, customer_id: int, pet: Pet) -> None:
        """
        Cancel any scheduled follow-up reminders (simulated).

        Args:
            customer_id: The customer ID
            pet: The pet entity
        """
        # In a real implementation, this would cancel scheduled reminder tasks
        self.logger.info(
            f"Reservation reminders cancelled for customer {customer_id} and pet {pet.technical_id}"
        )

    async def _send_cancellation_notification(self, customer_id: int, pet: Pet) -> None:
        """
        Send cancellation notification to customer (simulated).

        Args:
            customer_id: The customer ID
            pet: The pet entity
        """
        # In a real implementation, this would send an email or SMS
        self.logger.info(
            f"Cancellation notification sent to customer {customer_id} for pet {pet.name} ({pet.technical_id})"
        )
