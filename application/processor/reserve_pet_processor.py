"""
ReservePetProcessor for Purrfect Pets API

Handles the reservation of pets when they transition from available to pending,
setting reservation details and expiry times as specified in the Pet workflow.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReservePetProcessor(CyodaProcessor):
    """
    Processor for reserving Pet entities when they transition from available to pending.
    Sets reservation timestamp and expiry time for potential buyers.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReservePetProcessor",
            description="Reserve pet for potential buyer with expiry time",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for reservation.

        Args:
            entity: The Pet entity to reserve (must be in 'available' state)
            **kwargs: Additional processing parameters

        Returns:
            The reserved pet entity with reservation details
        """
        try:
            self.logger.info(
                f"Reserving Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Set reservation details
            self._set_reservation_details(pet)

            # Send notification (simulated)
            self._send_notification(pet)

            # Log reservation completion
            self.logger.info(
                f"Pet {pet.technical_id} reserved successfully until {pet.reservationExpiry}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error reserving pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _set_reservation_details(self, pet: Pet) -> None:
        """
        Set reservation timestamp and expiry time.

        Args:
            pet: The Pet entity to set reservation details for
        """
        current_time = datetime.now(timezone.utc)
        current_timestamp = current_time.isoformat().replace("+00:00", "Z")

        # Set reservation timestamp
        pet.reservedAt = current_timestamp

        # Set reservation expiry (24 hours from now)
        expiry_time = current_time + timedelta(hours=24)
        pet.reservationExpiry = expiry_time.isoformat().replace("+00:00", "Z")

        # Update timestamp
        pet.update_timestamp()

        self.logger.debug(
            f"Reservation details set for pet {pet.name}: "
            f"reservedAt={pet.reservedAt}, expires={pet.reservationExpiry}"
        )

    def _send_notification(self, pet: Pet) -> None:
        """
        Send notification about pet reservation (simulated).

        Args:
            pet: The Pet entity that was reserved
        """
        # In a real implementation, this would send an actual notification
        # For now, we just log the notification
        self.logger.info(
            f"NOTIFICATION: Pet '{pet.name}' (ID: {pet.technical_id}) has been reserved. "
            f"Reservation expires at {pet.reservationExpiry}"
        )

        # Could integrate with notification services like:
        # - Email service
        # - SMS service
        # - Push notification service
        # - Webhook to external systems
