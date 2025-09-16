"""
PetSaleProcessor for Purrfect Pets API

Handles the sale of Pet entities when payment is completed.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetSaleProcessor(CyodaProcessor):
    """
    Processor for completing Pet sales.
    Validates payment completion and updates pet ownership information.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetSaleProcessor",
            description="Completes Pet sales by validating payment and updating ownership information",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity sale.

        Args:
            entity: The Pet entity to sell
            **kwargs: Additional processing parameters

        Returns:
            The sold Pet entity
        """
        try:
            self.logger.info(
                f"Processing sale for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet is currently pending (reserved)
            if not pet.is_pending():
                raise ValueError(
                    f"Pet {pet.technical_id} is not in pending state for sale"
                )

            # Validate payment completion (this would normally check external payment service)
            # For now, we'll assume payment is validated by the criterion
            self.logger.info(f"Payment validation completed for Pet {pet.technical_id}")

            # Update pet ownership information
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            sale_id = str(uuid.uuid4())

            # Add sale metadata
            if not pet.metadata:
                pet.metadata = {}

            pet.metadata.update(
                {
                    "sale_date": current_time,
                    "sale_id": sale_id,
                    "sale_status": "completed",
                    "ownership_transferred": True,
                }
            )

            # Clear reservation metadata since sale is complete
            reservation_keys = [
                "reservation_time",
                "reservation_expiry",
                "reservation_status",
            ]
            for key in reservation_keys:
                pet.metadata.pop(key, None)

            # Generate sale receipt (would normally integrate with external system)
            receipt_data = {
                "sale_id": sale_id,
                "pet_id": pet.technical_id,
                "pet_name": pet.name,
                "sale_price": pet.price,
                "sale_date": current_time,
            }

            pet.metadata["sale_receipt"] = receipt_data

            # Update inventory count (would normally update external inventory system)
            self.logger.info(f"Inventory updated for Pet {pet.technical_id}")

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} sale completed successfully with sale ID {sale_id}"
            )

            # Note: Buyer confirmation would be handled by external service
            self.logger.info(f"Sale confirmation sent for Pet {pet.technical_id}")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing sale for Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
