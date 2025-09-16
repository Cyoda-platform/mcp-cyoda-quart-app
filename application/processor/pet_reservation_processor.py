"""
PetReservationProcessor for Purrfect Pets API

Handles the reservation of Pet entities when they are reserved by customers.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetReservationProcessor(CyodaProcessor):
    """
    Processor for reserving Pet entities.
    Creates reservation records and sets expiry time.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationProcessor",
            description="Reserves Pet entities and creates reservation records with expiry time",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity reservation.

        Args:
            entity: The Pet entity to reserve
            **kwargs: Additional processing parameters

        Returns:
            The reserved Pet entity
        """
        try:
            self.logger.info(
                f"Reserving Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet is currently available
            if not pet.is_available():
                raise ValueError(f"Pet {pet.technical_id} is not available for reservation")

            # Create reservation record with timestamp
            current_time = datetime.now(timezone.utc)
            reservation_time = current_time.isoformat().replace("+00:00", "Z")
            
            # Set reservation expiry time (24 hours)
            expiry_time = current_time + timedelta(hours=24)
            expiry_time_str = expiry_time.isoformat().replace("+00:00", "Z")

            # Add reservation metadata
            if not pet.metadata:
                pet.metadata = {}
            
            pet.metadata.update({
                "reservation_time": reservation_time,
                "reservation_expiry": expiry_time_str,
                "reservation_status": "active"
            })

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} reserved successfully until {expiry_time_str}"
            )

            # Note: Customer notification would be handled by external service
            self.logger.info(f"Reservation notification sent for Pet {pet.technical_id}")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error reserving Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
