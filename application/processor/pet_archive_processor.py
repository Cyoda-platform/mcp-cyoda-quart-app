"""Pet Archive Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class PetArchiveProcessor(CyodaProcessor):
    """Processor for archiving sold pets."""

    def __init__(self):
        super().__init__(
            name="PetArchiveProcessor",
            description="Archives sold pet, marks as unavailable",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process pet archiving."""
        try:
            if not isinstance(entity, Pet):
                raise ProcessorError(self.name, "Entity must be a Pet instance")

            # Validate pet is sold
            if entity.state not in ["sold"]:
                raise ProcessorError(
                    self.name,
                    f"Pet must be sold for archiving, current state: {entity.state}",
                )

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add archiving metadata
            entity.add_metadata("archived_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("archive_processed", True)
            entity.add_metadata("final_owner", entity.ownerId)

            logger.info(f"Successfully archived pet {entity.name}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process pet archiving for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process pet archiving: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Pet) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Pet"
        )
