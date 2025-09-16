"""
Subscriber Reactivation Processor for manually reactivating bounced subscribers.
"""

import logging
from typing import Any, Dict, Optional

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class SubscriberReactivationProcessor(CyodaProcessor):
    """Processor to manually reactivate bounced subscribers."""

    def __init__(
        self, name: str = "SubscriberReactivationProcessor", description: str = ""
    ):
        super().__init__(
            name=name,
            description=description or "Manually reactivates bounced subscriber",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process subscriber reactivation."""
        try:
            if not isinstance(entity, Subscriber):
                raise ProcessorError(
                    self.name, f"Expected Subscriber entity, got {type(entity)}"
                )

            # Validate subscriber exists and is in bounced state
            if entity.state != "bounced":
                raise ProcessorError(
                    self.name,
                    f"Subscriber must be in bounced state, current state: {entity.state}",
                )

            # Reactivate subscriber
            entity.isActive = True

            # Clear bounce metadata
            if entity.metadata:
                entity.metadata.pop("bounce_reason", None)
                entity.metadata.pop("bounced_at", None)

            # Add reactivation metadata
            entity.add_metadata("reactivated_at", entity.updated_at)
            entity.add_metadata("reactivation_reason", "Manual reactivation")

            logger.info(f"Reactivated subscriber: {entity.email}")
            return entity

        except Exception as e:
            logger.exception(f"Failed to reactivate subscriber {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to reactivate subscriber: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Subscriber)
