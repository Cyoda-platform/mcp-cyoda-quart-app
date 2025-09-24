"""
CompleteSaleProcessor for Purrfect Pets API

Handles the completion of pet sales when they transition from pending to sold,
recording sale details and updating inventory as specified in the Pet workflow.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CompleteSaleProcessor(CyodaProcessor):
    """
    Processor for completing Pet sales when they transition from pending to sold.
    Records sale timestamp, final price, and updates inventory.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CompleteSaleProcessor",
            description="Complete pet sale and update inventory records",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for sale completion.

        Args:
            entity: The Pet entity to complete sale for (must be in 'pending' state)
            **kwargs: Additional processing parameters

        Returns:
            The sold pet entity with sale completion details
        """
        try:
            self.logger.info(
                f"Completing sale for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Set sale completion details
            self._set_sale_details(pet)

            # Update inventory (simulated)
            self._update_inventory_count(pet)

            # Send notification (simulated)
            self._send_notification(pet)

            # Log sale completion
            self.logger.info(
                f"Pet {pet.technical_id} sale completed successfully for ${pet.soldPrice}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error completing sale for pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _set_sale_details(self, pet: Pet) -> None:
        """
        Set sale completion timestamp and final price.

        Args:
            pet: The Pet entity to set sale details for
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Set sale timestamp
        pet.soldAt = current_timestamp

        # Set sold price (use current price if available, otherwise 0)
        pet.soldPrice = pet.price if pet.price is not None else 0.0

        # Update timestamp
        pet.update_timestamp()

        self.logger.debug(
            f"Sale details set for pet {pet.name}: "
            f"soldAt={pet.soldAt}, soldPrice=${pet.soldPrice}"
        )

    def _update_inventory_count(self, pet: Pet) -> None:
        """
        Update inventory count (simulated).

        Args:
            pet: The Pet entity that was sold
        """
        # In a real implementation, this would update actual inventory systems
        # For now, we just log the inventory update
        self.logger.info(
            f"INVENTORY UPDATE: Pet '{pet.name}' (ID: {pet.technical_id}) "
            f"removed from available inventory. Category: {pet.category.get('name', 'Unknown') if pet.category else 'Unknown'}"
        )

        # Could integrate with inventory management systems:
        # - Update database inventory counts
        # - Sync with external inventory systems
        # - Update analytics and reporting systems
        # - Trigger reorder notifications if needed

    def _send_notification(self, pet: Pet) -> None:
        """
        Send notification about completed sale (simulated).

        Args:
            pet: The Pet entity that was sold
        """
        # In a real implementation, this would send actual notifications
        # For now, we just log the notification
        self.logger.info(
            f"NOTIFICATION: Pet '{pet.name}' (ID: {pet.technical_id}) has been sold "
            f"for ${pet.soldPrice}. Sale completed at {pet.soldAt}"
        )

        # Could integrate with notification services:
        # - Email confirmation to buyer
        # - SMS notifications
        # - Update customer management systems
        # - Trigger fulfillment processes
        # - Update financial/accounting systems
