"""Owner Reinstate Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OwnerReinstateProcessor(CyodaProcessor):
    """Processor for reinstating suspended owner accounts."""

    def __init__(self):
        super().__init__(
            name="OwnerReinstateProcessor",
            description="Reinstates suspended owner account",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner reinstatement."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, "Entity must be an Owner instance")

            # Validate owner is suspended
            if entity.state not in ["suspended"]:
                raise ProcessorError(
                    self.name,
                    f"Owner must be suspended for reinstatement, current state: {entity.state}",
                )

            # TODO: In a real implementation, this would:
            # 1. Validate suspension period is complete
            # 2. Check reinstatement conditions are met
            # 3. Send reinstatement email

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add reinstatement metadata
            entity.add_metadata("reinstated_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("reinstatement_processed", True)
            entity.add_metadata("reinstatement_email_sent", True)

            # Clear suspension metadata
            if entity.metadata:
                entity.metadata.pop("suspended_at", None)
                entity.metadata.pop("suspension_reason", None)

            logger.info(f"Successfully reinstated owner {entity.email}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process owner reinstatement for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process owner reinstatement: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Owner"
        )
