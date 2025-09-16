"""
EmailDelivery Retry Processor for retrying failed email deliveries.
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


class EmailDeliveryRetryProcessor(CyodaProcessor):
    """Processor to retry failed email deliveries."""

    def __init__(
        self, name: str = "EmailDeliveryRetryProcessor", description: str = ""
    ):
        super().__init__(
            name=name, description=description or "Retries failed email delivery"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Retry failed email delivery."""
        try:
            if not isinstance(entity, EmailDelivery):
                raise ProcessorError(
                    self.name, f"Expected EmailDelivery entity, got {type(entity)}"
                )

            # Validate email delivery is in failed state
            if entity.state != "failed":
                raise ProcessorError(
                    self.name,
                    f"EmailDelivery must be in failed state to retry, current state: {entity.state}",
                )

            # Validate retry attempts are within limit
            max_retry_attempts = 3
            if entity.deliveryAttempts >= max_retry_attempts:
                raise ProcessorError(
                    self.name, f"Maximum retry attempts ({max_retry_attempts}) exceeded"
                )

            # Clear error message for retry
            entity.errorMessage = None
            entity.lastAttemptDate = datetime.now(timezone.utc)

            # Add retry metadata
            entity.add_metadata(
                "retry_attempted_at", entity.lastAttemptDate.isoformat()
            )
            entity.add_metadata("retry_count", entity.deliveryAttempts)

            logger.info(
                f"Retrying email delivery for subscriber {entity.subscriberId} (attempt {entity.deliveryAttempts + 1})"
            )
            return entity

        except Exception as e:
            logger.exception(f"Failed to retry email delivery {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to retry email delivery: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, EmailDelivery)
