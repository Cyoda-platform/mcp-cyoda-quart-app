"""
EmailDelivery Open Processor for tracking email opening.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.emaildelivery.version_1.emaildelivery import \
    EmailDelivery
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class EmailDeliveryOpenProcessor(CyodaProcessor):
    """Processor to track email opening."""

    def __init__(self, name: str = "EmailDeliveryOpenProcessor", description: str = ""):
        super().__init__(name=name, description=description or "Tracks email opening")

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Track email opening."""
        try:
            if not isinstance(entity, EmailDelivery):
                raise ProcessorError(
                    self.name, f"Expected EmailDelivery entity, got {type(entity)}"
                )

            # Validate email was delivered
            if entity.state != "delivered":
                raise ProcessorError(
                    self.name,
                    f"Email must be delivered before tracking open, current state: {entity.state}",
                )

            # Set open details
            entity.opened = True
            entity.openedDate = datetime.now(timezone.utc)

            # Add open tracking metadata
            entity.add_metadata("open_tracked_at", entity.openedDate.isoformat())
            entity.add_metadata("open_tracking_method", "Tracking pixel")

            logger.info(f"Tracked email open for subscriber {entity.subscriberId}")
            return entity

        except Exception as e:
            logger.exception(f"Failed to track email open {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to track email open: {str(e)}", e)

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, EmailDelivery)
