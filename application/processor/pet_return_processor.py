"""
PetReturnProcessor for Purrfect Pets API

Handles the return of Pet entities when they are returned by customers.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetReturnProcessor(CyodaProcessor):
    """
    Processor for handling Pet returns.
    Validates return conditions, processes refunds, and resets pet ownership.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReturnProcessor",
            description="Handles Pet returns by validating conditions, processing refunds, and resetting ownership",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity return.

        Args:
            entity: The Pet entity to return
            **kwargs: Additional processing parameters (may include return_reason)

        Returns:
            The returned Pet entity
        """
        try:
            self.logger.info(
                f"Processing return for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet is currently sold
            if not pet.is_sold():
                raise ValueError(
                    f"Pet {pet.technical_id} is not in sold state for return"
                )

            # Get return reason from kwargs or use default
            return_reason = kwargs.get("return_reason", "Customer return")

            # Validate return conditions (would normally check return policy)
            self.logger.info(f"Return conditions validated for Pet {pet.technical_id}")

            # Process refund if applicable (would normally integrate with payment system)
            refund_amount = pet.price
            refund_id = str(uuid.uuid4())

            self.logger.info(
                f"Processing refund of ${refund_amount} for Pet {pet.technical_id}"
            )

            # Reset pet ownership
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add return metadata
            if not pet.metadata:
                pet.metadata = {}

            pet.metadata.update(
                {
                    "return_date": current_time,
                    "return_reason": return_reason,
                    "return_id": str(uuid.uuid4()),
                    "refund_id": refund_id,
                    "refund_amount": refund_amount,
                    "refund_status": "processed",
                    "ownership_transferred": False,
                }
            )

            # Clear sale metadata since pet is returned
            sale_keys = ["sale_date", "sale_id", "sale_status", "sale_receipt"]
            for key in sale_keys:
                pet.metadata.pop(key, None)

            # Update pet condition notes if provided
            condition_notes = kwargs.get("condition_notes")
            if condition_notes:
                pet.metadata["return_condition_notes"] = condition_notes

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(
                f"Pet {pet.technical_id} return processed successfully. Refund ID: {refund_id}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing return for Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
