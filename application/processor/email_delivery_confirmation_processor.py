"""
EmailDeliveryConfirmationProcessor for Cyoda Client Application

Confirms email delivery (tracking) and marks as delivered.
"""

import logging
from typing import Any, cast

from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class EmailDeliveryConfirmationProcessor(CyodaProcessor):
    """Processor for confirming email delivery."""

    def __init__(self) -> None:
        super().__init__(
            name="EmailDeliveryConfirmationProcessor",
            description="Confirms email delivery (tracking)",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process email delivery confirmation."""
        try:
            email_delivery = cast_entity(entity, EmailDelivery)

            if email_delivery.state != "sent":
                raise ValueError(
                    f"Email delivery must be in sent state, current state: {email_delivery.state}"
                )

            email_delivery.update_timestamp()

            self.logger.info(
                f"Email delivery confirmed for subscriber {email_delivery.subscriber_id}"
            )

            return email_delivery
        except Exception as e:
            self.logger.error(f"Error processing email delivery confirmation: {str(e)}")
            raise
