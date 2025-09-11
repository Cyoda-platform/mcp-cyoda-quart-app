"""
EmailRetryProcessor for Cyoda Client Application

Retries failed email delivery by resetting error state.
"""

import logging
from typing import Any, cast

from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class EmailRetryProcessor(CyodaProcessor):
    """Processor for retrying failed email deliveries."""

    def __init__(self) -> None:
        super().__init__(
            name="EmailRetryProcessor",
            description="Retries failed email delivery",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process email delivery retry."""
        try:
            email_delivery = cast_entity(entity, EmailDelivery)

            if not email_delivery.can_retry():
                raise ValueError("Email delivery cannot be retried")

            email_delivery.reset_for_retry()

            self.logger.info(
                f"Email delivery reset for retry (attempt {email_delivery.delivery_attempts + 1}/3)"
            )

            return email_delivery
        except Exception as e:
            self.logger.error(f"Error processing email retry: {str(e)}")
            raise
