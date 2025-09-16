"""
EmailDelivery Bounce Processor for handling permanent email bounces.
"""

import logging
from typing import Any, Dict, Optional

from application.entity.emaildelivery.version_1.emaildelivery import \
    EmailDelivery
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class EmailDeliveryBounceProcessor(CyodaProcessor):
    """Processor to handle permanent email bounces."""

    def __init__(
        self, name: str = "EmailDeliveryBounceProcessor", description: str = ""
    ):
        super().__init__(
            name=name, description=description or "Handles permanent email bounce"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Handle permanent email bounce."""
        try:
            if not isinstance(entity, EmailDelivery):
                raise ProcessorError(
                    self.name, f"Expected EmailDelivery entity, got {type(entity)}"
                )

            # Get bounce details from kwargs
            bounce_reason = kwargs.get("bounce_reason", "Hard bounce detected")

            # Set bounce details
            entity.errorMessage = bounce_reason

            # Add bounce metadata
            entity.add_metadata("bounced_at", entity.updated_at)
            entity.add_metadata("bounce_type", "hard")
            entity.add_metadata("bounce_reason", bounce_reason)

            # Trigger subscriber bounce workflow
            entity_service = self._get_entity_service()
            try:
                # Get subscriber and trigger bounce transition
                subscriber_response = await entity_service.get_by_id(
                    str(entity.subscriberId), "subscriber", "1"
                )
                if subscriber_response:
                    # This would trigger the subscriber bounce workflow
                    # In a real implementation, this would be handled by the workflow engine
                    entity.add_metadata("subscriber_bounce_triggered", True)
            except Exception as e:
                logger.error(
                    f"Failed to trigger subscriber bounce for subscriber {entity.subscriberId}: {e}"
                )

            logger.warning(
                f"Email bounced for subscriber {entity.subscriberId}: {bounce_reason}"
            )
            return entity

        except Exception as e:
            logger.exception(f"Failed to process email bounce {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to process email bounce: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, EmailDelivery)

    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service

        return get_entity_service()
