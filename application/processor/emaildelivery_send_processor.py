"""
EmailDelivery Send Processor for sending emails to subscribers.
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


class EmailDeliverySendProcessor(CyodaProcessor):
    """Processor to send emails to subscribers."""

    def __init__(self, name: str = "EmailDeliverySendProcessor", description: str = ""):
        super().__init__(
            name=name, description=description or "Sends email to subscriber"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Send email to subscriber."""
        try:
            if not isinstance(entity, EmailDelivery):
                raise ProcessorError(
                    self.name, f"Expected EmailDelivery entity, got {type(entity)}"
                )

            # Get entity service to fetch subscriber and cat fact details
            entity_service = self._get_entity_service()

            # Get subscriber details
            subscriber_response = await entity_service.get_by_id(
                str(entity.subscriberId), "subscriber", "1"
            )
            subscriber_data = subscriber_response.data

            # Get cat fact details
            catfact_response = await entity_service.get_by_id(
                str(entity.catFactId), "catfact", "1"
            )
            catfact_data = catfact_response.data

            # Compose email content
            email_content = self._compose_email(subscriber_data, catfact_data, entity.entity_id or "")

            # Simulate email sending (in real implementation, use actual email service)
            success = await self._send_email(
                subscriber_data.get("email"), email_content
            )

            if success:
                # Update delivery details
                entity.sentDate = datetime.now(timezone.utc)
                entity.deliveryAttempts += 1
                entity.lastAttemptDate = entity.sentDate

                logger.info(
                    f"Sent email to {subscriber_data.get('email')} for cat fact {entity.catFactId}"
                )
            else:
                raise ProcessorError(self.name, "Email send failed")

            return entity

        except Exception as e:
            logger.exception(f"Failed to send email delivery {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to send email: {str(e)}", e)

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, EmailDelivery)

    def _compose_email(
        self, subscriber_data: Dict[str, Any], catfact_data: Dict[str, Any], delivery_id: str = ""
    ) -> Dict[str, str]:
        """Compose email content."""
        subject = "Your Weekly Cat Fact"

        body = f"""
        Hello {subscriber_data.get('firstName', 'Cat Lover')}!

        Here's your weekly cat fact:

        {catfact_data.get('fact')}

        Enjoy your week!

        ---
        To unsubscribe, click here: [unsubscribe link with token {subscriber_data.get('unsubscribeToken')}]
        """

        return {
            "subject": subject,
            "body": body,
            "tracking_pixel": f"[tracking pixel for delivery {delivery_id}]",
        }

    async def _send_email(self, email: str, content: Dict[str, str]) -> bool:
        """Send email via email service (simulated)."""
        # In real implementation, integrate with actual email service
        # For now, simulate successful sending
        logger.info(f"Simulating email send to {email}: {content['subject']}")
        return True

    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service

        return get_entity_service()
