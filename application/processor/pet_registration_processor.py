"""Pet Registration Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class PetRegistrationProcessor(CyodaProcessor):
    """Processor for registering new pets."""

    def __init__(self):
        super().__init__(
            name="PetRegistrationProcessor",
            description="Validates pet data, assigns unique ID, sets creation timestamp, initializes pet as available",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet registration."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(self.name, "Entity must be a Pet instance")

            # Validate required fields
            if not entity.name or not entity.name.strip():
                raise ProcessorError(self.name, "Pet name is required")

            if not entity.category or not entity.category.strip():
                raise ProcessorError(self.name, "Pet category is required")

            if entity.price <= 0:
                raise ProcessorError(self.name, "Pet price must be positive")

            if entity.age < 0:
                raise ProcessorError(self.name, "Pet age must be non-negative")

            if entity.weight <= 0:
                raise ProcessorError(self.name, "Pet weight must be positive")

            # Set timestamps
            current_time = datetime.now(timezone.utc).isoformat()
            entity.createdAt = current_time
            entity.updatedAt = current_time
            entity.update_timestamp()

            # Initialize metadata
            entity.add_metadata("registration_processed", True)
            entity.add_metadata("processed_at", current_time)

            logger.info(f"Successfully processed pet registration for {entity.name}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process pet registration for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process pet registration: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Pet"
        )
