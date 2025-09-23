"""
EmailCampaignReportingProcessor for Cat Fact Subscription Application

Handles the final reporting and completion of email campaigns.
Calculates final metrics and marks campaigns as completed.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.email_campaign.version_1.email_campaign import EmailCampaign
from services.services import get_entity_service


class EmailCampaignReportingProcessor(CyodaProcessor):
    """
    Processor for EmailCampaign that handles final reporting and completion.
    Calculates metrics and finalizes campaign status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignReportingProcessor",
            description="Finalizes email campaigns and generates completion reports",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the EmailCampaign to finalize reporting and mark as completed.

        Args:
            entity: The EmailCampaign to process (must be in 'sending' state)
            **kwargs: Additional processing parameters

        Returns:
            The completed campaign with final metrics
        """
        try:
            self.logger.info(
                f"Finalizing campaign reporting for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Mark cat fact as used if campaign was successful
            if campaign.emails_sent > 0:
                await self._mark_cat_fact_as_used(campaign.cat_fact_id, campaign.technical_id)

            # Complete the campaign (this calculates final metrics)
            campaign.complete_campaign()

            # Generate completion report
            report = self._generate_campaign_report(campaign)
            
            self.logger.info(
                f"Campaign {campaign.technical_id} completed successfully. Report: {report}"
            )

            return campaign

        except Exception as e:
            self.logger.error(
                f"Error finalizing campaign {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark campaign as failed
            if hasattr(entity, 'fail_campaign'):
                entity.fail_campaign(f"Reporting failed: {str(e)}")
            raise

    async def _mark_cat_fact_as_used(self, cat_fact_id: str, campaign_id: str) -> None:
        """Mark the cat fact as used in this campaign."""
        try:
            entity_service = get_entity_service()
            
            # Get the cat fact
            result = await entity_service.get_by_id(
                entity_id=cat_fact_id,
                entity_class="CatFact",
                entity_version="1",
            )

            if result:
                # Update cat fact to mark as used
                cat_fact_data = result.data
                if hasattr(cat_fact_data, 'model_dump'):
                    cat_fact_dict = cat_fact_data.model_dump(by_alias=True)
                else:
                    cat_fact_dict = dict(cat_fact_data) if hasattr(cat_fact_data, '__dict__') else cat_fact_data

                # Mark as used
                cat_fact_dict['isUsed'] = True
                cat_fact_dict['usedInCampaignId'] = campaign_id
                
                from datetime import datetime, timezone
                cat_fact_dict['usedAt'] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

                # Update with transition to 'used' state
                await entity_service.update(
                    entity_id=cat_fact_id,
                    entity=cat_fact_dict,
                    entity_class="CatFact",
                    entity_version="1",
                    transition="use"
                )

                self.logger.info(f"Marked cat fact {cat_fact_id} as used in campaign {campaign_id}")

        except Exception as e:
            self.logger.error(f"Error marking cat fact as used: {str(e)}")

    def _generate_campaign_report(self, campaign: EmailCampaign) -> dict:
        """Generate a summary report for the completed campaign."""
        return {
            "campaign_id": campaign.technical_id,
            "campaign_name": campaign.campaign_name,
            "campaign_date": campaign.campaign_date,
            "total_subscribers": campaign.total_subscribers,
            "emails_sent": campaign.emails_sent,
            "emails_failed": campaign.emails_failed,
            "emails_opened": campaign.emails_opened,
            "emails_clicked": campaign.emails_clicked,
            "delivery_rate": campaign.delivery_rate,
            "open_rate": campaign.open_rate,
            "click_rate": campaign.click_rate,
            "success_rate": campaign.get_success_rate(),
            "status": campaign.status,
            "completed_at": campaign.completed_at
        }
