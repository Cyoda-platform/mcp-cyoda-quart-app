"""
PetReservationProcessor for Purrfect Pets API

Handles the reservation process for pets, including creating reservation records,
updating pet status, and managing reservation data.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetReservationProcessor(CyodaProcessor):
    """
    Processor for handling pet reservations in the adoption workflow.
    Creates reservation records and updates pet status to reserved.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationProcessor",
            description="Processes pet reservations and updates adoption status"
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the pet reservation.

        Args:
            entity: The Pet entity to process (must be in 'available' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed pet with reservation data
        """
        try:
            self.logger.info(
                f"Processing pet reservation for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Create reservation data
            reservation_data = self._create_reservation_data(pet)
            pet.reservation_data = reservation_data

            # Update adoption status
            pet.adoption_status = "Reserved"
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} reserved successfully with reservation ID {reservation_data['reservation_id']}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet reservation for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_reservation_data(self, pet: Pet) -> Dict[str, Any]:
        """
        Create reservation data for the pet.

        Args:
            pet: The Pet entity being reserved

        Returns:
            Dictionary containing reservation information
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        reservation_id = str(uuid.uuid4())

        # Calculate reservation expiry (7 days from now)
        expiry_date = datetime.now(timezone.utc)
        expiry_date = expiry_date.replace(day=expiry_date.day + 7)
        expiry_timestamp = expiry_date.isoformat().replace("+00:00", "Z")

        reservation_data: Dict[str, Any] = {
            "reservation_id": reservation_id,
            "reserved_at": current_timestamp,
            "expires_at": expiry_timestamp,
            "status": "ACTIVE",
            "pet_id": pet.technical_id or pet.entity_id,
            "pet_name": pet.name,
            "reservation_fee": float(pet.price * 0.1),  # 10% reservation fee
            "notes": f"Reservation for {pet.name} ({pet.species}, {pet.breed})"
        }

        return reservation_data

    def _determine_reservation_priority(self, pet: Pet) -> str:
        """
        Determine reservation priority based on pet characteristics.

        Args:
            pet: The Pet entity

        Returns:
            Priority level: HIGH, MEDIUM, or LOW
        """
        # High priority for young pets or special needs
        if pet.age_months < 6 or pet.special_needs:
            return "HIGH"
        # Medium priority for popular breeds
        elif pet.species in ["Dog", "Cat"] and pet.health_status == "Healthy":
            return "MEDIUM"
        else:
            return "LOW"
