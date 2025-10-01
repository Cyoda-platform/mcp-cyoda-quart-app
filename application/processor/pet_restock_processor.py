"""
PetRestockProcessor for Cyoda Petstore Application

Handles restocking of Pet entities when they transition from sold back to available.
Manages inventory replenishment and restock-related business logic.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service


class PetRestockProcessor(CyodaProcessor):
    """
    Processor for Pet restocking that handles the transition from sold to available,
    updates inventory levels, and manages restock-related business logic.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetRestockProcessor",
            description="Processes Pet restocking, updates inventory and handles restock operations",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for restocking.

        Args:
            entity: The Pet entity to restock (should be in 'sold' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with updated restock data
        """
        try:
            self.logger.info(
                f"Processing Pet restock for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Process restock data
            restock_data = self._create_restock_data(pet)
            pet.processed_data = restock_data

            # Update inventory for restock
            self._process_restock_inventory(pet)

            # Log restock completion
            self.logger.info(
                f"Pet {pet.technical_id} restock processed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet restock {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_restock_data(self, pet: Pet) -> Dict[str, Any]:
        """
        Create restock processing data.

        Args:
            pet: The Pet entity being restocked

        Returns:
            Dictionary containing restock processing data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        restock_id = str(uuid.uuid4())

        # Determine restock quantity based on pet breed and category
        restock_quantity = self._calculate_restock_quantity(pet)

        # Create restock processing data
        restock_data: Dict[str, Any] = {
            "restock_processed_at": current_timestamp,
            "restock_id": restock_id,
            "restock_status": "COMPLETED",
            "original_inventory": pet.inventory_count or 0,
            "restock_quantity": restock_quantity,
            "new_inventory": (pet.inventory_count or 0) + restock_quantity,
            "pet_name": pet.name,
            "pet_breed": pet.breed or "UNKNOWN",
            "restock_reason": "MANUAL_RESTOCK",
        }

        return restock_data

    def _calculate_restock_quantity(self, pet: Pet) -> int:
        """
        Calculate appropriate restock quantity based on pet characteristics.

        Args:
            pet: The Pet entity being restocked

        Returns:
            Restock quantity
        """
        # Base restock quantity
        base_quantity = 10
        
        # Adjust based on breed popularity (simplified logic)
        popular_breeds = ["LABRADOR", "GOLDEN_RETRIEVER", "GERMAN_SHEPHERD", "BULLDOG"]
        if pet.breed in popular_breeds:
            base_quantity = 15
        
        # Adjust based on price (higher price = lower stock)
        if pet.price and pet.price > 1000:
            base_quantity = max(5, base_quantity - 5)
        
        return base_quantity

    def _process_restock_inventory(self, pet: Pet) -> None:
        """
        Update inventory after restock completion.

        Args:
            pet: The Pet entity being restocked
        """
        # Calculate restock quantity
        restock_quantity = self._calculate_restock_quantity(pet)
        
        # Update inventory
        current_inventory = pet.inventory_count or 0
        new_inventory = current_inventory + restock_quantity
        
        pet.inventory_count = new_inventory
        
        # Update status to available since we now have stock
        pet.status = "available"
        
        # Update timestamp
        pet.update_timestamp()
        
        self.logger.info(
            f"Pet {pet.technical_id} restocked: {current_inventory} -> {new_inventory} (+{restock_quantity})"
        )
