"""
EmailCampaign Processors for Cat Facts Subscription System

Handles email campaign scheduling, sending, and analysis.
"""

import logging
from datetime import datetime, timezone
from typing import Any, List

from application.entity.cat_fact.version_1.cat_fact import CatFact
from application.entity.email_campaign.version_1.email_campaign import EmailCampaign
from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class EmailCampaignSchedulingProcessor(CyodaProcessor):
    """
    Processor for scheduling email campaigns.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignSchedulingProcessor",
            description="Schedules email campaigns and prepares target subscriber lists",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process email campaign scheduling.

        Args:
            entity: The EmailCampaign entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed email campaign entity
        """
        try:
            self.logger.info(
                f"Processing email campaign scheduling for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Get target subscribers
            target_count = await self._count_target_subscribers(campaign)
            campaign.target_subscriber_count = target_count

            # Set default email subject if not provided
            if not campaign.email_subject:
                campaign.email_subject = await self._generate_email_subject(campaign)

            # Set scheduled time if not provided
            if not campaign.scheduled_at:
                campaign.scheduled_at = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            campaign.update_timestamp()

            self.logger.info(
                f"Email campaign {campaign.technical_id} scheduled for {target_count} subscribers"
            )

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error processing email campaign scheduling {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _count_target_subscribers(self, campaign: EmailCampaign) -> int:
        """
        Count the number of target subscribers for the campaign.

        Args:
            campaign: The email campaign

        Returns:
            Number of target subscribers
        """
        try:
            entity_service = get_entity_service()

            # Get all active subscribers
            subscribers = await entity_service.find_all(
                entity_class=Subscriber.ENTITY_NAME,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )

            # Filter for active subscribers
            active_count = 0
            for subscriber_response in subscribers:
                subscriber = cast_entity(subscriber_response.data, Subscriber)
                if subscriber.is_active_subscriber():
                    active_count += 1

            return active_count

        except Exception as e:
            self.logger.warning(f"Could not count target subscribers: {str(e)}")
            return 0

    async def _generate_email_subject(self, campaign: EmailCampaign) -> str:
        """
        Generate email subject line for the campaign.

        Args:
            campaign: The email campaign

        Returns:
            Generated email subject
        """
        if campaign.campaign_type == "weekly":
            return "🐱 Your Weekly Cat Fact is Here!"
        elif campaign.campaign_type == "daily":
            return "🐾 Daily Cat Fact"
        elif campaign.campaign_type == "monthly":
            return "📅 Monthly Cat Facts Roundup"
        else:
            return "🐱 Interesting Cat Fact"


class EmailCampaignSendingProcessor(CyodaProcessor):
    """
    Processor for sending email campaigns to subscribers.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignSendingProcessor",
            description="Sends email campaigns to target subscribers",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process email campaign sending.

        Args:
            entity: The EmailCampaign entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed email campaign entity
        """
        try:
            self.logger.info(
                f"Processing email campaign sending for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Start the campaign
            campaign.start_campaign()

            # Get the cat fact to send
            cat_fact = await self._get_cat_fact(campaign.cat_fact_id)
            if not cat_fact:
                raise ValueError(f"Cat fact {campaign.cat_fact_id} not found")

            # Get target subscribers
            subscribers = await self._get_target_subscribers(campaign)

            # Send emails to all subscribers
            await self._send_emails_to_subscribers(campaign, cat_fact, subscribers)

            # Complete the campaign
            campaign.complete_campaign()

            self.logger.info(
                f"Email campaign {campaign.technical_id} completed. Sent {campaign.emails_sent} emails"
            )

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error processing email campaign sending {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_cat_fact(self, cat_fact_id: str) -> CatFact:
        """
        Get the cat fact for the campaign.

        Args:
            cat_fact_id: ID of the cat fact

        Returns:
            The cat fact entity
        """
        entity_service = get_entity_service()

        response = await entity_service.get_by_id(
            entity_id=cat_fact_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        if response:
            return cast_entity(response.data, CatFact)
        return None

    async def _get_target_subscribers(
        self, campaign: EmailCampaign
    ) -> List[Subscriber]:
        """
        Get target subscribers for the campaign.

        Args:
            campaign: The email campaign

        Returns:
            List of target subscribers
        """
        entity_service = get_entity_service()

        # Get all subscribers
        subscribers_response = await entity_service.find_all(
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        # Filter for active subscribers
        active_subscribers = []
        for subscriber_response in subscribers_response:
            subscriber = cast_entity(subscriber_response.data, Subscriber)
            if subscriber.is_active_subscriber():
                active_subscribers.append(subscriber)

        return active_subscribers

    async def _send_emails_to_subscribers(
        self, campaign: EmailCampaign, cat_fact: CatFact, subscribers: List[Subscriber]
    ) -> None:
        """
        Send emails to all target subscribers.

        Args:
            campaign: The email campaign
            cat_fact: The cat fact to send
            subscribers: List of target subscribers
        """
        entity_service = get_entity_service()

        for subscriber in subscribers:
            try:
                # Simulate sending email
                await self._send_email_to_subscriber(campaign, cat_fact, subscriber)

                # Record successful send
                campaign.record_email_sent()

                # Update subscriber stats
                subscriber.record_email_sent()

                # Update subscriber in database
                await entity_service.update(
                    entity_id=subscriber.technical_id or subscriber.entity_id,
                    entity=subscriber.model_dump(by_alias=True),
                    entity_class=Subscriber.ENTITY_NAME,
                    entity_version=str(Subscriber.ENTITY_VERSION),
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to send email to {subscriber.email}: {str(e)}"
                )
                campaign.record_email_failed(str(e))

    async def _send_email_to_subscriber(
        self, campaign: EmailCampaign, cat_fact: CatFact, subscriber: Subscriber
    ) -> None:
        """
        Send email to a single subscriber.

        Args:
            campaign: The email campaign
            cat_fact: The cat fact to send
            subscriber: The target subscriber
        """
        # In a real implementation, this would integrate with an email service
        self.logger.info(
            f"Sending email to {subscriber.email} with cat fact: {cat_fact.fact_text[:50]}..."
        )

        # Simulate email sending delay
        import asyncio

        await asyncio.sleep(0.01)  # Small delay to simulate email sending

        self.logger.debug(f"Email sent successfully to {subscriber.email}")


class EmailCampaignAnalysisProcessor(CyodaProcessor):
    """
    Processor for analyzing email campaign performance.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignAnalysisProcessor",
            description="Analyzes email campaign performance and generates reports",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process email campaign analysis.

        Args:
            entity: The EmailCampaign entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed email campaign entity
        """
        try:
            self.logger.info(
                f"Processing email campaign analysis for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Generate performance summary
            performance = campaign.get_performance_summary()

            # Log performance metrics
            self.logger.info(
                f"Campaign {campaign.technical_id} performance: "
                f"Delivery Rate: {performance['delivery_rate']:.2%}, "
                f"Open Rate: {performance['open_rate']:.2%}, "
                f"Click Rate: {performance['click_rate']:.2%}"
            )

            # Add analysis metadata
            campaign.add_metadata(
                "analysis_completed_at",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )
            campaign.add_metadata("performance_summary", performance)

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error processing email campaign analysis {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
