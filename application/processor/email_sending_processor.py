"""
EmailSendingProcessor for Cat Fact Subscription Application

Handles the sending of email campaigns to active subscribers.
Manages the email delivery process and tracks sending statistics.
"""

import logging
from typing import Any, List

from application.entity.email_campaign.version_1.email_campaign import EmailCampaign
from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class EmailSendingProcessor(CyodaProcessor):
    """
    Processor for EmailCampaign that handles sending emails to active subscribers
    and tracks delivery statistics.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailSendingProcessor",
            description="Sends email campaigns to active subscribers and tracks delivery",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EmailCampaign to send emails to active subscribers.

        Args:
            entity: The EmailCampaign to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed campaign with updated sending statistics
        """
        try:
            self.logger.info(
                f"Starting email sending for campaign {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Mark campaign as started
            campaign.start_campaign()

            # Get active subscribers
            active_subscribers = await self._get_active_subscribers()
            campaign.total_subscribers = len(active_subscribers)

            self.logger.info(
                f"Found {len(active_subscribers)} active subscribers for campaign {campaign.technical_id}"
            )

            # Get cat fact content
            cat_fact_content = await self._get_cat_fact_content(campaign.cat_fact_id)
            if cat_fact_content:
                campaign.cat_fact_text = cat_fact_content

            # Send emails to subscribers
            sent_count = 0
            failed_count = 0

            for subscriber in active_subscribers:
                try:
                    # Simulate email sending (in real implementation, this would use an email service)
                    success = await self._send_email_to_subscriber(
                        subscriber, campaign, cat_fact_content
                    )

                    if success:
                        sent_count += 1
                        # Update subscriber statistics
                        if subscriber.technical_id:
                            await self._update_subscriber_stats(
                                subscriber.technical_id, sent=True
                            )
                    else:
                        failed_count += 1

                except Exception as e:
                    self.logger.error(
                        f"Failed to send email to subscriber {subscriber.technical_id}: {str(e)}"
                    )
                    failed_count += 1

            # Update campaign statistics
            campaign.update_email_stats(sent=sent_count, failed=failed_count)

            self.logger.info(
                f"Email sending completed for campaign {campaign.technical_id}: "
                f"{sent_count} sent, {failed_count} failed"
            )

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error processing email campaign {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_active_subscribers(self) -> List[Subscriber]:
        """Get all active subscribers from the database."""
        try:
            entity_service = get_entity_service()

            # Search for active subscribers
            builder = SearchConditionRequest.builder()
            builder.equals("subscriptionStatus", "active")
            condition = builder.build()

            results = await entity_service.search(
                entity_class=Subscriber.ENTITY_NAME,
                condition=condition,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )

            subscribers = []
            for result in results:
                try:
                    subscriber = cast_entity(result.data, Subscriber)
                    subscribers.append(subscriber)
                except Exception as e:
                    self.logger.warning(f"Failed to cast subscriber entity: {str(e)}")
                    continue

            return subscribers

        except Exception as e:
            self.logger.error(f"Error getting active subscribers: {str(e)}")
            return []

    async def _get_cat_fact_content(self, cat_fact_id: str) -> str:
        """Get cat fact content by ID."""
        try:
            entity_service = get_entity_service()

            result = await entity_service.get_by_id(
                entity_id=cat_fact_id,
                entity_class="CatFact",
                entity_version="1",
            )

            if result and hasattr(result.data, "fact_text"):
                return result.data.fact_text
            elif result and isinstance(result.data, dict):
                return result.data.get("factText", "No cat fact available")
            else:
                return "No cat fact available"

        except Exception as e:
            self.logger.error(f"Error getting cat fact content: {str(e)}")
            return "No cat fact available"

    async def _send_email_to_subscriber(
        self, subscriber: Subscriber, campaign: EmailCampaign, cat_fact: str
    ) -> bool:
        """
        Send email to a single subscriber.
        In a real implementation, this would integrate with an email service like SendGrid, AWS SES, etc.
        """
        try:
            # Simulate email sending logic
            self.logger.info(
                f"Sending email to {subscriber.email} for campaign {campaign.campaign_name}"
            )

            # In real implementation, you would:
            # 1. Format the email template with cat fact content
            # 2. Send via email service API
            # 3. Handle delivery confirmations
            # 4. Track opens and clicks

            # For now, we'll simulate successful sending
            return True

        except Exception as e:
            self.logger.error(f"Error sending email to {subscriber.email}: {str(e)}")
            return False

    async def _update_subscriber_stats(
        self, subscriber_id: str, sent: bool = False, opened: bool = False
    ) -> None:
        """Update subscriber email statistics."""
        try:
            entity_service = get_entity_service()

            # Get current subscriber
            result = await entity_service.get_by_id(
                entity_id=subscriber_id,
                entity_class=Subscriber.ENTITY_NAME,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )

            if result:
                subscriber = cast_entity(result.data, Subscriber)
                subscriber.update_email_stats(sent=sent, opened=opened)

                # Update subscriber in database
                await entity_service.update(
                    entity_id=subscriber_id,
                    entity=subscriber.model_dump(by_alias=True),
                    entity_class=Subscriber.ENTITY_NAME,
                    entity_version=str(Subscriber.ENTITY_VERSION),
                )

        except Exception as e:
            self.logger.error(f"Error updating subscriber stats: {str(e)}")
