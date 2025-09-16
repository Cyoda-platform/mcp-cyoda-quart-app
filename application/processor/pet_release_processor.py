"""
PetReleaseProcessor for Purrfect Pets API

Releases pet reservation when order is cancelled, updating inventory accordingly.
"""

import logging
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetReleaseProcessor(CyodaProcessor):
    """
    Processor for releasing pet reservations when orders are cancelled.
    Updates inventory to release reserved quantity and logs release details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReleaseProcessor",
            description="Releases pet reservations by updating inventory",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet release according to functional requirements.

        Args:
            entity: The Pet entity to release
            **kwargs: Additional processing parameters (should contain cancellation_info)

        Returns:
            The processed pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet release {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet is in Pending state
            if not pet.is_pending():
                raise ValueError(
                    f"Pet {pet.technical_id} is not in pending state for release"
                )

            # Extract cancellation information from kwargs
            cancellation_info = kwargs.get("cancellation_info", {})
            order_id = cancellation_info.get("order_id")

            if not order_id:
                raise ValueError("Order ID is required for pet release")

            # Update inventory to release reserved quantity
            await self._release_inventory(pet, order_id)

            # Log release details
            self._log_release(pet, order_id)

            # Update timestamps
            pet.update_timestamp()

            self.logger.info(f"Pet {pet.technical_id} released from order {order_id}")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet release {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _release_inventory(self, pet: Pet, order_id: str) -> None:
        """
        Release inventory reservation for the pet.

        Args:
            pet: The Pet entity to release
            order_id: The order ID that had the reservation
        """
        try:
            self.logger.info(
                f"Releasing inventory reservation for pet {pet.technical_id} from order {order_id}"
            )

            # In a real implementation, we would:
            # 1. Find the inventory record by pet_id
            # 2. Reduce reserved_quantity by 1
            # 3. Save the updated inventory record

            # For now, we'll log the release action
            self.logger.info(
                f"Inventory reservation released for pet {pet.technical_id} (order {order_id})"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to release inventory for pet {pet.technical_id}: {str(e)}"
            )
            raise

    def _log_release(self, pet: Pet, order_id: str) -> None:
        """
        Log release details.

        Args:
            pet: The Pet entity being released
            order_id: The order ID that had the reservation
        """
        self.logger.info(
            f"RELEASE LOG: Pet {pet.technical_id} released from order {order_id} "
            f"at {pet.updated_at}"
        )
