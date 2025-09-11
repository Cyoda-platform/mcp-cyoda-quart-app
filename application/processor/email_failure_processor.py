"""
EmailFailureProcessor for Cyoda Client Application

Handles email sending failure and schedules retries if applicable.
"""

import logging
from typing import Any, cast

from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class EmailFailureProcessor(CyodaProcessor):
    """Processor for handling email delivery failures."""

    def __init__(self) -> None:
        super().__init__(
            name="EmailFailureProcessor",
            description="Handles email sending failure",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process email delivery failure."""
        try:
            email_delivery = cast_entity(entity, EmailDelivery)
            error_message = kwargs.get("error_message", "Unknown error")

            email_delivery.mark_failed(error_message)

            self.logger.warning(f"Email delivery failed: {error_message}")

            if email_delivery.can_retry():
                self.logger.info(
                    f"Email delivery can be retried (attempt {email_delivery.delivery_attempts}/3)"
                )
            else:
                self.logger.error(
                    f"Email delivery failed permanently after {email_delivery.delivery_attempts} attempts"
                )

            return email_delivery
        except Exception as e:
            self.logger.error(f"Error processing email failure: {str(e)}")
            raise
