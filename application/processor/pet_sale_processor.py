"""
PetSaleProcessor for Cyoda Petstore Application

Handles the sale processing for Pet entities when they transition from
pending to sold status. Manages inventory updates and sale-related business logic.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class PetSaleProcessor(CyodaProcessor):
    """
    Processor for Pet sales that handles the transition from pending to sold,
    updates inventory, and manages sale-related business logic.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetSaleProcessor",
            description="Processes Pet sales, updates inventory and handles sale completion",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for sale completion.

        Args:
            entity: The Pet entity to process (should be in 'pending' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with updated sale data
        """
        try:
            self.logger.info(
                f"Processing Pet sale for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Process sale data
            sale_data = self._create_sale_data(pet)
            pet.processed_data = sale_data

            # Update inventory for sale
            self._process_sale_inventory(pet)

            # Log sale completion
            self.logger.info(f"Pet {pet.technical_id} sale processed successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet sale {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_sale_data(self, pet: Pet) -> Dict[str, Any]:
        """
        Create sale processing data.

        Args:
            pet: The Pet entity being sold

        Returns:
            Dictionary containing sale processing data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        sale_id = str(uuid.uuid4())

        # Create sale processing data
        sale_data: Dict[str, Any] = {
            "sale_processed_at": current_timestamp,
            "sale_id": sale_id,
            "sale_status": "COMPLETED",
            "original_inventory": pet.inventory_count or 0,
            "sale_price": pet.price or 0.0,
            "pet_name": pet.name,
            "pet_breed": pet.breed or "UNKNOWN",
            "inventory_after_sale": max(0, (pet.inventory_count or 0) - 1),
        }

        return sale_data

    def _process_sale_inventory(self, pet: Pet) -> None:
        """
        Update inventory after sale completion.

        Args:
            pet: The Pet entity being sold
        """
        # Reduce inventory by 1 for the sale
        current_inventory = pet.inventory_count or 0
        new_inventory = max(0, current_inventory - 1)

        pet.inventory_count = new_inventory

        # Update status to sold if inventory reaches zero
        if new_inventory == 0:
            pet.status = "sold"
            self.logger.info(
                f"Pet {pet.technical_id} marked as sold - inventory depleted"
            )

        # Update timestamp
        pet.update_timestamp()

        self.logger.info(
            f"Pet {pet.technical_id} inventory updated: {current_inventory} -> {new_inventory}"
        )
