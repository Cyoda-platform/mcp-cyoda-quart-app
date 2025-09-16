"""Owner Activation Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OwnerActivationProcessor(CyodaProcessor):
    """Processor for reactivating owner accounts."""

    def __init__(self):
        super().__init__(
            name="OwnerActivationProcessor", description="Reactivates owner account"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner activation."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, "Entity must be an Owner instance")

            # Validate owner is inactive
            if entity.state not in ["inactive"]:
                raise ProcessorError(
                    self.name,
                    f"Owner must be inactive for activation, current state: {entity.state}",
                )

            # TODO: In a real implementation, this would:
            # 1. Validate owner account is in good standing
            # 2. Check for any outstanding issues
            # 3. Send reactivation email

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add activation metadata
            entity.add_metadata(
                "reactivated_at", datetime.now(timezone.utc).isoformat()
            )
            entity.add_metadata("activation_processed", True)
            entity.add_metadata("reactivation_email_sent", True)

            # Clear deactivation metadata
            if entity.metadata:
                entity.metadata.pop("deactivated_at", None)
                entity.metadata.pop("deactivation_reason", None)

            logger.info(f"Successfully reactivated owner {entity.email}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process owner activation for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process owner activation: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Owner"
        )
