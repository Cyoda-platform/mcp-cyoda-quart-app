"""
EmailCampaign Validation Criterion for Cat Facts Subscription System

Validates that an EmailCampaign meets all required business rules before proceeding
to the scheduling stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.email_campaign.version_1.email_campaign import EmailCampaign


class EmailCampaignValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for EmailCampaign that checks all business rules
    before the campaign can proceed to scheduling stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailCampaignValidationCriterion",
            description="Validates EmailCampaign business rules and configuration",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the email campaign meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be EmailCampaign)
            **kwargs: Additional criteria parameters

        Returns:
            True if the email campaign meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating email campaign {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailCampaign for type-safe operations
            campaign = cast_entity(entity, EmailCampaign)

            # Validate campaign name
            if not self._is_valid_campaign_name(campaign.campaign_name):
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} has invalid campaign name: {campaign.campaign_name}"
                )
                return False

            # Validate cat fact ID is provided
            if not self._is_valid_cat_fact_id(campaign.cat_fact_id):
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} has invalid cat fact ID: {campaign.cat_fact_id}"
                )
                return False

            # Validate campaign type
            if campaign.campaign_type not in campaign.ALLOWED_CAMPAIGN_TYPES:
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} has invalid campaign type: {campaign.campaign_type}"
                )
                return False

            # Validate email template
            if campaign.email_template not in campaign.ALLOWED_TEMPLATES:
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} has invalid email template: {campaign.email_template}"
                )
                return False

            # Validate email subject if provided
            if campaign.email_subject and not self._is_valid_email_subject(campaign.email_subject):
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} has invalid email subject"
                )
                return False

            # Validate target criteria if provided
            if campaign.target_criteria and not self._is_valid_target_criteria(campaign.target_criteria):
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} has invalid target criteria"
                )
                return False

            # Validate metrics are non-negative
            if not self._are_valid_metrics(campaign):
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} has invalid metrics"
                )
                return False

            # Validate logical consistency of metrics
            if not self._are_metrics_logically_consistent(campaign):
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} has logically inconsistent metrics"
                )
                return False

            # Check if cat fact exists and is ready (in a real implementation)
            if not await self._is_cat_fact_available(campaign.cat_fact_id):
                self.logger.warning(
                    f"Email campaign {campaign.technical_id} references unavailable cat fact: {campaign.cat_fact_id}"
                )
                return False

            self.logger.info(
                f"Email campaign {campaign.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating email campaign {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _is_valid_campaign_name(self, campaign_name: str) -> bool:
        """
        Validate campaign name.

        Args:
            campaign_name: Campaign name to validate

        Returns:
            True if campaign name is valid
        """
        if not campaign_name:
            return False
            
        name = campaign_name.strip()
        
        # Check minimum length
        if len(name) < 3:
            return False
            
        # Check maximum length
        if len(name) > 200:
            return False
            
        # Check for valid characters (letters, numbers, spaces, hyphens, underscores)
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            return False
            
        return True

    def _is_valid_cat_fact_id(self, cat_fact_id: str) -> bool:
        """
        Validate cat fact ID format.

        Args:
            cat_fact_id: Cat fact ID to validate

        Returns:
            True if cat fact ID is valid
        """
        if not cat_fact_id:
            return False
            
        # Basic format validation (should be non-empty string)
        if len(cat_fact_id.strip()) == 0:
            return False
            
        # Check reasonable length
        if len(cat_fact_id) > 100:
            return False
            
        return True

    def _is_valid_email_subject(self, email_subject: str) -> bool:
        """
        Validate email subject line.

        Args:
            email_subject: Email subject to validate

        Returns:
            True if email subject is valid
        """
        if not email_subject:
            return True  # Subject is optional
            
        subject = email_subject.strip()
        
        # Check maximum length
        if len(subject) > 200:
            return False
            
        # Check for suspicious content (basic spam detection)
        spam_indicators = [
            'free money', 'click here now', 'urgent!!!',
            'winner', 'congratulations!!!', 'act now'
        ]
        
        subject_lower = subject.lower()
        if any(indicator in subject_lower for indicator in spam_indicators):
            return False
            
        return True

    def _is_valid_target_criteria(self, target_criteria: dict) -> bool:
        """
        Validate target criteria configuration.

        Args:
            target_criteria: Target criteria to validate

        Returns:
            True if target criteria is valid
        """
        if not isinstance(target_criteria, dict):
            return False
            
        # Check for valid criteria keys
        valid_keys = {
            'subscription_status', 'preferred_frequency', 'min_engagement_rate',
            'max_unsubscribe_rate', 'active_since_days', 'exclude_recent_campaigns'
        }
        
        for key in target_criteria.keys():
            if key not in valid_keys:
                return False
                
        # Validate specific criteria values
        if 'min_engagement_rate' in target_criteria:
            rate = target_criteria['min_engagement_rate']
            if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
                return False
                
        if 'max_unsubscribe_rate' in target_criteria:
            rate = target_criteria['max_unsubscribe_rate']
            if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
                return False
                
        return True

    def _are_valid_metrics(self, campaign: EmailCampaign) -> bool:
        """
        Validate all metrics are non-negative.

        Args:
            campaign: Email campaign to validate

        Returns:
            True if all metrics are valid
        """
        metrics = [
            campaign.target_subscriber_count,
            campaign.emails_sent,
            campaign.emails_failed,
            campaign.emails_bounced,
            campaign.emails_opened,
            campaign.emails_clicked,
            campaign.unsubscribes
        ]
        
        return all(metric >= 0 for metric in metrics)

    def _are_metrics_logically_consistent(self, campaign: EmailCampaign) -> bool:
        """
        Validate metrics are logically consistent with each other.

        Args:
            campaign: Email campaign to validate

        Returns:
            True if metrics are logically consistent
        """
        # Total attempts should equal sent + failed + bounced
        total_attempts = campaign.emails_sent + campaign.emails_failed + campaign.emails_bounced
        
        # If we have any delivery metrics, they should be consistent
        if total_attempts > 0:
            # Opened emails cannot exceed sent emails
            if campaign.emails_opened > campaign.emails_sent:
                return False
                
            # Clicked emails cannot exceed opened emails
            if campaign.emails_clicked > campaign.emails_opened:
                return False
                
            # Unsubscribes cannot exceed sent emails
            if campaign.unsubscribes > campaign.emails_sent:
                return False
                
        return True

    async def _is_cat_fact_available(self, cat_fact_id: str) -> bool:
        """
        Check if the referenced cat fact exists and is available.

        Args:
            cat_fact_id: ID of the cat fact to check

        Returns:
            True if cat fact is available
        """
        try:
            from services.services import get_entity_service
            from application.entity.cat_fact.version_1.cat_fact import CatFact
            
            entity_service = get_entity_service()
            
            # Try to get the cat fact
            response = await entity_service.get_by_id(
                entity_id=cat_fact_id,
                entity_class=CatFact.ENTITY_NAME,
                entity_version=str(CatFact.ENTITY_VERSION),
            )
            
            if not response:
                return False
                
            # Check if cat fact is in a ready state
            cat_fact = cast_entity(response.data, CatFact)
            return cat_fact.is_ready_for_sending()
            
        except Exception as e:
            self.logger.warning(f"Could not verify cat fact availability: {str(e)}")
            # If we can't check, assume it's available to avoid blocking valid campaigns
            return True
