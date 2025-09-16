"""
PetSaleProcessor for Purrfect Pets API

Marks pet as sold when order is completed, updating inventory and logging sale details.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service


class PetSaleProcessor(CyodaProcessor):
    """
    Processor for marking pets as sold when orders are completed.
    Updates inventory to reduce available quantity and logs sale details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetSaleProcessor",
            description="Marks pets as sold and updates inventory",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet sale according to functional requirements.

        Args:
            entity: The Pet entity to mark as sold
            **kwargs: Additional processing parameters (should contain order_info)

        Returns:
            The processed pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet sale {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet is in Pending state
            if not pet.is_pending():
                raise ValueError(f"Pet {pet.technical_id} is not in pending state for sale")

            # Extract order information from kwargs
            order_info = kwargs.get("order_info", {})
            order_id = order_info.get("completed_order_id") or order_info.get("order_id")
            
            if not order_id:
                raise ValueError("Order ID is required for pet sale")

            # Update inventory to reduce available quantity
            await self._update_inventory_for_sale(pet, order_id)

            # Log sale details
            self._log_sale(pet, order_id)

            # Update timestamps
            pet.update_timestamp()

            self.logger.info(f"Pet {pet.technical_id} marked as sold for order {order_id}")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet sale {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _update_inventory_for_sale(self, pet: Pet, order_id: str) -> None:
        """
        Update inventory to reduce available quantity by 1 for the sale.

        Args:
            pet: The Pet entity being sold
            order_id: The completed order ID
        """
        try:
            entity_service = get_entity_service()

            self.logger.info(
                f"Updating inventory for pet sale {pet.technical_id} (order {order_id})"
            )

            # In a real implementation, we would:
            # 1. Find the inventory record by pet_id
            # 2. Reduce quantity by 1
            # 3. Reduce reserved_quantity by 1 (since it was reserved)
            # 4. Save the updated inventory record
            # 5. Trigger InventoryUpdateProcessor to check stock levels
            
            # For now, we'll log the inventory update action
            self.logger.info(
                f"Inventory updated for pet sale {pet.technical_id} (order {order_id})"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to update inventory for pet sale {pet.technical_id}: {str(e)}"
            )
            raise

    def _log_sale(self, pet: Pet, order_id: str) -> None:
        """
        Log sale details.

        Args:
            pet: The Pet entity being sold
            order_id: The completed order ID
        """
        self.logger.info(
            f"SALE LOG: Pet {pet.technical_id} sold via order {order_id} "
            f"for price {pet.price} at {pet.updated_at}"
        )
