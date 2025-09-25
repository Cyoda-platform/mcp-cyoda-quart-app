"""
PetProcessor for Purrfect Pets API Application

Handles the main business logic for processing Pet instances.
Enriches pet data and performs pet-related calculations.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service


class PetProcessor(CyodaProcessor):
    """
    Processor for Pet entity that handles main business logic,
    enriches pet data, and performs pet-related processing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetProcessor",
            description="Processes Pet instances, enriches data and performs pet-related calculations",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet according to business requirements.

        Args:
            entity: The Pet to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with enriched data
        """
        try:
            self.logger.info(
                f"Processing Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Enrich pet with processed data
            processed_data = self._create_processed_data(pet)
            pet.processed_data = processed_data

            # Update pet status if needed
            await self._update_pet_status(pet)

            # Log processing completion
            self.logger.info(
                f"Pet {pet.technical_id} processed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_processed_data(self, pet: Pet) -> Dict[str, Any]:
        """
        Create processed data for the pet.

        Args:
            pet: The Pet to process

        Returns:
            Dictionary containing processed data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        processing_id = str(uuid.uuid4())

        # Create processed data with pet-specific enrichments
        processed_data: Dict[str, Any] = {
            "processed_at": current_timestamp,
            "processing_id": processing_id,
            "processing_status": "COMPLETED",
            "enriched_category": pet.category_name.upper() if pet.category_name else "UNKNOWN",
            "photo_count": len(pet.photo_urls),
            "tag_count": len(pet.tags),
            "has_description": bool(pet.description),
            "has_price": bool(pet.price),
        }

        # Add age-based classification
        if pet.age is not None:
            if pet.age < 1:
                processed_data["age_category"] = "PUPPY/KITTEN"
            elif pet.age < 7:
                processed_data["age_category"] = "ADULT"
            else:
                processed_data["age_category"] = "SENIOR"
        else:
            processed_data["age_category"] = "UNKNOWN"

        return processed_data

    async def _update_pet_status(self, pet: Pet) -> None:
        """
        Update pet status based on business rules.

        Args:
            pet: The processed Pet
        """
        # Simple business logic: if pet has no photos and is available, mark as pending
        if pet.status == "available" and not pet.photo_urls:
            self.logger.info(
                f"Pet {pet.technical_id} marked as pending due to missing photos"
            )
            # Note: We don't update the current entity via EntityService
            # The entity will be updated automatically when we return from the processor
            pet.status = "pending"
            pet.update_timestamp()
