"""
PetProcessor for Cyoda Client Application

Handles the business logic for processing Pet instances ingested from the pet store API.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetProcessor(CyodaProcessor):
    """
    Processor for Pet that handles main business logic for processing
    pet data ingested from the pet store API.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetProcessor",
            description="Processes Pet instances ingested from the pet store API",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity according to functional requirements.

        Args:
            entity: The Pet to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with enriched data
        """
        try:
            self.logger.info(
                f"Processing Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            pet = cast_entity(entity, Pet)

            processing_result = self._create_processing_result(pet)
            pet.set_processing_result(processing_result)

            self.logger.info(f"Pet {pet.technical_id} processed successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_processing_result(self, pet: Pet) -> Dict[str, Any]:
        """
        Create processing result for the pet.

        Args:
            pet: The Pet to process

        Returns:
            Dictionary containing processing result
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        processing_result: Dict[str, Any] = {
            "processed_at": current_timestamp,
            "pet_name": pet.name,
            "pet_type": pet.pet_type,
            "status": pet.status,
            "processing_status": "COMPLETED",
        }

        if pet.tags:
            processing_result["tag_count"] = len(pet.tags)

        if pet.photo_urls:
            processing_result["photo_count"] = len(pet.photo_urls)

        if pet.price is not None:
            processing_result["price_processed"] = pet.price

        return processing_result
