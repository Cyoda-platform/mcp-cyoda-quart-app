"""
PetInventoryProcessor for Cyoda Petstore Application

Handles inventory management and processing for Pet entities.
Updates inventory counts, manages stock levels, and handles business logic
for pet availability and inventory tracking.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service


class PetInventoryProcessor(CyodaProcessor):
    """
    Processor for Pet inventory management that handles stock tracking,
    availability updates, and inventory-related business logic.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetInventoryProcessor",
            description="Processes Pet inventory, manages stock levels and availability",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for inventory management.

        Args:
            entity: The Pet entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with updated inventory data
        """
        try:
            self.logger.info(
                f"Processing Pet inventory for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Process inventory data
            processed_data = self._create_inventory_data(pet)
            pet.processed_data = processed_data

            # Update inventory status based on business rules
            self._update_inventory_status(pet)

            # Log processing completion
            self.logger.info(
                f"Pet {pet.technical_id} inventory processed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet inventory {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_inventory_data(self, pet: Pet) -> Dict[str, Any]:
        """
        Create inventory processing data.

        Args:
            pet: The Pet entity to process

        Returns:
            Dictionary containing inventory processing data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        processing_id = str(uuid.uuid4())

        # Create inventory processing data
        inventory_data: Dict[str, Any] = {
            "processed_at": current_timestamp,
            "processing_id": processing_id,
            "inventory_status": "PROCESSED",
            "stock_level": pet.inventory_count or 0,
            "availability_status": self._determine_availability_status(pet),
            "reorder_needed": (pet.inventory_count or 0) < 5,
            "last_inventory_check": current_timestamp,
        }

        return inventory_data

    def _determine_availability_status(self, pet: Pet) -> str:
        """
        Determine availability status based on inventory and pet status.

        Args:
            pet: The Pet entity

        Returns:
            Availability status string
        """
        inventory_count = pet.inventory_count or 0
        
        if pet.status == "sold" or inventory_count == 0:
            return "OUT_OF_STOCK"
        elif inventory_count < 5:
            return "LOW_STOCK"
        elif inventory_count < 20:
            return "MODERATE_STOCK"
        else:
            return "HIGH_STOCK"

    def _update_inventory_status(self, pet: Pet) -> None:
        """
        Update pet status based on inventory levels.

        Args:
            pet: The Pet entity to update
        """
        inventory_count = pet.inventory_count or 0
        
        # Update status based on inventory
        if inventory_count == 0 and pet.status != "sold":
            pet.status = "sold"
            self.logger.info(f"Pet {pet.technical_id} status updated to 'sold' due to zero inventory")
        elif inventory_count > 0 and pet.status == "sold":
            pet.status = "available"
            self.logger.info(f"Pet {pet.technical_id} status updated to 'available' due to restocking")
        
        # Update timestamp
        pet.update_timestamp()
