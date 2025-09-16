"""
Subscriber Activation Processor for activating pending subscribers.
"""

import logging
from typing import Any, Dict, Optional

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class SubscriberActivationProcessor(CyodaProcessor):
    """Processor to activate pending subscribers."""

    def __init__(
        self, name: str = "SubscriberActivationProcessor", description: str = ""
    ):
        super().__init__(
            name=name,
            description=description
            or "Activates subscriber after email verification or auto-activation",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process subscriber activation."""
        try:
            if not isinstance(entity, Subscriber):
                raise ProcessorError(
                    self.name, f"Expected Subscriber entity, got {type(entity)}"
                )

            # Validate subscriber is in pending state
            if entity.state not in ["pending", "initial_state"]:
                raise ProcessorError(
                    self.name,
                    f"Subscriber must be in pending state, current state: {entity.state}",
                )

            # Activate subscriber
            entity.isActive = True

            logger.info(f"Activated subscriber: {entity.email}")
            return entity

        except Exception as e:
            logger.exception(f"Failed to activate subscriber {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to activate subscriber: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Subscriber)
