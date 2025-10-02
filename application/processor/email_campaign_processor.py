"""
Email Campaign Processors for Cat Fact Subscription Application

Handles email campaign creation, scheduling, sending, and completion.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.email_campaign.version_1.email_campaign import EmailCampaign
from application.entity.subscriber.version_1.subscriber import Subscriber
from services.services import get_entity_service


class EmailCampaignCreationProcessor(CyodaProcessor):
    """
    Processor for creating email campaigns.
    Sets up initial campaign data and validates configuration.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignCreationProcessor",
            description="Creates email campaigns and sets up initial configuration",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process email campaign creation.

        Args:
            entity: The EmailCampaign entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed email campaign entity
        """
        try:
            self.logger.info(
                f"Creating email campaign {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Set default campaign type if not provided
            if not campaign.campaign_type:
                campaign.campaign_type = "weekly_cat_fact"

            # Generate default subject line if not provided
            if not campaign.subject_line:
                campaign.subject_line = "Your Weekly Cat Fact! 🐱"

            self.logger.info(
                f"Email campaign {campaign.campaign_name} created successfully"
            )

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error creating email campaign {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class EmailCampaignSchedulingProcessor(CyodaProcessor):
    """
    Processor for scheduling email campaigns.
    Counts target subscribers and prepares for sending.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignSchedulingProcessor",
            description="Schedules email campaigns and counts target subscribers",
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
                f"Scheduling email campaign {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Count active subscribers
            subscriber_count = await self._count_active_subscribers()
            campaign.target_subscriber_count = subscriber_count

            self.logger.info(
                f"Email campaign {campaign.campaign_name} scheduled for {subscriber_count} subscribers"
            )

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error scheduling email campaign {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _count_active_subscribers(self) -> int:
        """
        Count the number of active subscribers.
        
        Returns:
            Number of active subscribers
        """
        try:
            entity_service = get_entity_service()
            
            # Get all subscribers
            subscribers = await entity_service.find_all(
                entity_class=Subscriber.ENTITY_NAME,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )
            
            # Count active subscribers
            active_count = 0
            for subscriber_response in subscribers:
                subscriber = cast_entity(subscriber_response.data, Subscriber)
                if subscriber.is_eligible_for_email():
                    active_count += 1
            
            return active_count
            
        except Exception as e:
            self.logger.error(f"Error counting active subscribers: {str(e)}")
            return 0


class EmailCampaignSendingProcessor(CyodaProcessor):
    """
    Processor for sending email campaigns.
    Simulates email sending to subscribers.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignSendingProcessor",
            description="Sends email campaigns to subscribers",
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
                f"Sending email campaign {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Send emails to subscribers
            await self._send_emails_to_subscribers(campaign)

            # Mark campaign as sent
            campaign.mark_as_sent()

            self.logger.info(
                f"Email campaign {campaign.campaign_name} sent to {campaign.emails_sent} subscribers"
            )

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error sending email campaign {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_emails_to_subscribers(self, campaign: EmailCampaign) -> None:
        """
        Send emails to all active subscribers.
        
        Args:
            campaign: The email campaign to send
        """
        try:
            entity_service = get_entity_service()
            
            # Get all subscribers
            subscribers = await entity_service.find_all(
                entity_class=Subscriber.ENTITY_NAME,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )
            
            # Send to each active subscriber
            for subscriber_response in subscribers:
                subscriber = cast_entity(subscriber_response.data, Subscriber)
                
                if subscriber.is_eligible_for_email():
                    # Simulate email sending
                    success = await self._simulate_email_send(subscriber, campaign)
                    
                    if success:
                        campaign.record_email_sent()
                        # Update subscriber's email tracking
                        subscriber.record_email_sent()
                        
                        # Update subscriber in the system
                        await entity_service.update(
                            entity_id=subscriber.technical_id,
                            entity=subscriber.model_dump(by_alias=True),
                            entity_class=Subscriber.ENTITY_NAME,
                            entity_version=str(Subscriber.ENTITY_VERSION),
                        )
                    else:
                        campaign.record_email_failed("Email delivery failed")
            
        except Exception as e:
            self.logger.error(f"Error sending emails to subscribers: {str(e)}")
            campaign.record_email_failed(f"Bulk send error: {str(e)}")

    async def _simulate_email_send(self, subscriber: Subscriber, campaign: EmailCampaign) -> bool:
        """
        Simulate sending an email to a subscriber.
        
        Args:
            subscriber: The subscriber to send to
            campaign: The campaign being sent
            
        Returns:
            True if successful, False otherwise
        """
        # Simulate email sending (in real implementation, this would use an email service)
        self.logger.info(f"Simulating email send to {subscriber.email} for campaign {campaign.campaign_name}")
        
        # Simulate 95% success rate
        import random
        return random.random() < 0.95


class EmailCampaignCompletionProcessor(CyodaProcessor):
    """
    Processor for completing email campaigns.
    Finalizes metrics and cleanup.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignCompletionProcessor",
            description="Completes email campaigns and finalizes metrics",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process email campaign completion.

        Args:
            entity: The EmailCampaign entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed email campaign entity
        """
        try:
            self.logger.info(
                f"Completing email campaign {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Mark campaign as completed
            campaign.mark_as_completed()

            self.logger.info(
                f"Email campaign {campaign.campaign_name} completed with {campaign.get_success_rate_percentage():.1f}% success rate"
            )

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error completing email campaign {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
