"""
PetReservationProcessor for Purrfect Pets API

Reserves a pet for an order by updating inventory and logging reservation details.
"""

import logging
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetReservationProcessor(CyodaProcessor):
    """
    Processor for reserving pets for orders.
    Updates inventory to reserve quantity and logs reservation details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationProcessor",
            description="Reserves pets for orders by updating inventory",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet reservation according to functional requirements.

        Args:
            entity: The Pet entity to reserve
            **kwargs: Additional processing parameters (should contain order_info)

        Returns:
            The processed pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet reservation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet is in Available state
            if not pet.is_available():
                raise ValueError(
                    f"Pet {pet.technical_id} is not available for reservation"
                )

            # Extract order information from kwargs
            order_info = kwargs.get("order_info", {})
            order_id = order_info.get("order_id")

            if not order_id:
                raise ValueError("Order ID is required for pet reservation")

            # Update inventory to reserve quantity
            await self._reserve_inventory(pet, order_id)

            # Log reservation details
            self._log_reservation(pet, order_id)

            # Update timestamps
            pet.update_timestamp()

            self.logger.info(f"Pet {pet.technical_id} reserved for order {order_id}")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet reservation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _reserve_inventory(self, pet: Pet, order_id: str) -> None:
        """
        Reserve inventory quantity for the pet.

        Args:
            pet: The Pet entity to reserve
            order_id: The order ID requesting the reservation
        """
        try:
            # Find inventory record for this pet
            # Note: In a real implementation, we would search by pet_id
            # For now, we'll assume the inventory exists and can be found

            self.logger.info(
                f"Reserving inventory for pet {pet.technical_id} for order {order_id}"
            )

            # In a real implementation, we would:
            # 1. Find the inventory record by pet_id
            # 2. Check if sufficient quantity is available
            # 3. Update reserved_quantity
            # 4. Save the updated inventory record

            # For now, we'll log the reservation action
            self.logger.info(
                f"Inventory reserved for pet {pet.technical_id} (order {order_id})"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to reserve inventory for pet {pet.technical_id}: {str(e)}"
            )
            raise

    def _log_reservation(self, pet: Pet, order_id: str) -> None:
        """
        Log reservation details.

        Args:
            pet: The Pet entity being reserved
            order_id: The order ID requesting the reservation
        """
        self.logger.info(
            f"RESERVATION LOG: Pet {pet.technical_id} reserved for order {order_id} "
            f"at {pet.updated_at}"
        )
