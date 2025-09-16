"""
EmailDelivery Failure Processor for handling email delivery failures.
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


class EmailDeliveryFailureProcessor(CyodaProcessor):
    """Processor to handle email delivery failures."""

    def __init__(
        self, name: str = "EmailDeliveryFailureProcessor", description: str = ""
    ):
        super().__init__(
            name=name, description=description or "Handles email delivery failure"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Handle email delivery failure."""
        try:
            if not isinstance(entity, EmailDelivery):
                raise ProcessorError(
                    self.name, f"Expected EmailDelivery entity, got {type(entity)}"
                )

            # Get failure details from kwargs
            failure_reason = kwargs.get("failure_reason", "Unknown delivery failure")

            # Update failure details
            entity.deliveryAttempts += 1
            entity.lastAttemptDate = datetime.now(timezone.utc)
            entity.errorMessage = failure_reason

            # Check if max retry limit reached
            max_retry_attempts = 3
            if entity.deliveryAttempts >= max_retry_attempts:
                # Trigger subscriber bounce if permanent failure
                if self._is_permanent_failure(failure_reason):
                    entity_service = self._get_entity_service()
                    # This would trigger subscriber bounce workflow
                    entity.add_metadata("permanent_failure", True)
                    entity.add_metadata("bounce_subscriber", True)

            logger.warning(
                f"Email delivery failed for subscriber {entity.subscriberId}: {failure_reason}"
            )
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process email delivery failure {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process email delivery failure: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, EmailDelivery)

    def _is_permanent_failure(self, failure_reason: str) -> bool:
        """Check if failure is permanent."""
        permanent_indicators = [
            "hard bounce",
            "permanent failure",
            "invalid email",
            "mailbox does not exist",
            "domain not found",
            "recipient rejected",
        ]
        return any(
            indicator in failure_reason.lower() for indicator in permanent_indicators
        )

    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service

        return get_entity_service()
