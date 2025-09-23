"""
EmailCampaignValidationCriterion for Cat Fact Subscription Application

Validates that an EmailCampaign meets all required business rules before it can
proceed to the sending stage as specified in functional requirements.
"""

from typing import Any

from application.entity.email_campaign.version_1.email_campaign import EmailCampaign
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class EmailCampaignValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for EmailCampaign that checks all business rules
    before the entity can proceed to sending stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignValidationCriterion",
            description="Validates EmailCampaign configuration and readiness for sending",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the email campaign meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be EmailCampaign)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating email campaign {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Validate campaign name
            if not campaign.campaign_name or len(campaign.campaign_name.strip()) == 0:
                self.logger.warning(
                    f"EmailCampaign {campaign.technical_id} has empty campaign name"
                )
                return False

            # Validate campaign date format
            if not campaign.campaign_date:
                self.logger.warning(
                    f"EmailCampaign {campaign.technical_id} has empty campaign date"
                )
                return False

            try:
                from datetime import datetime

                datetime.strptime(campaign.campaign_date, "%Y-%m-%d")
            except ValueError:
                self.logger.warning(
                    f"EmailCampaign {campaign.technical_id} has invalid campaign date format: {campaign.campaign_date}"
                )
                return False

            # Validate cat fact ID
            if not campaign.cat_fact_id or len(campaign.cat_fact_id.strip()) == 0:
                self.logger.warning(
                    f"EmailCampaign {campaign.technical_id} has empty cat fact ID"
                )
                return False

            # Validate status
            if campaign.status not in ["created", "sending", "completed", "failed"]:
                self.logger.warning(
                    f"EmailCampaign {campaign.technical_id} has invalid status: {campaign.status}"
                )
                return False

            # Validate email subject
            if not campaign.email_subject or len(campaign.email_subject.strip()) == 0:
                self.logger.warning(
                    f"EmailCampaign {campaign.technical_id} has empty email subject"
                )
                return False

            # Validate email template
            if not campaign.email_template or len(campaign.email_template.strip()) == 0:
                self.logger.warning(
                    f"EmailCampaign {campaign.technical_id} has empty email template"
                )
                return False

            # Check that campaign is not already completed or failed
            if campaign.status in ["completed", "failed"]:
                self.logger.warning(
                    f"EmailCampaign {campaign.technical_id} is already {campaign.status}"
                )
                return False

            self.logger.info(
                f"EmailCampaign {campaign.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating email campaign {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
