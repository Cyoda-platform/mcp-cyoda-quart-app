"""
Subscriber Validation Criterion for Cat Facts Subscription System

Validates that a Subscriber meets all required business rules before proceeding
to the confirmation stage.
"""

import re
from typing import Any

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class SubscriberValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Subscriber that checks all business rules
    before the subscriber can proceed to confirmation stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberValidationCriterion",
            description="Validates Subscriber business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the subscriber meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Subscriber)
            **kwargs: Additional criteria parameters

        Returns:
            True if the subscriber meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating subscriber {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Validate email format
            if not self._is_valid_email(subscriber.email):
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} has invalid email format: {subscriber.email}"
                )
                return False

            # Validate email domain (basic check for common domains)
            if not self._is_allowed_email_domain(subscriber.email):
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} has disallowed email domain: {subscriber.email}"
                )
                return False

            # Validate subscription status
            if subscriber.subscription_status not in subscriber.ALLOWED_STATUSES:
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} has invalid subscription status: {subscriber.subscription_status}"
                )
                return False

            # Validate preferred frequency
            if subscriber.preferred_frequency not in subscriber.ALLOWED_FREQUENCIES:
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} has invalid preferred frequency: {subscriber.preferred_frequency}"
                )
                return False

            # Validate name fields if provided
            if not self._are_valid_names(subscriber.first_name or "", subscriber.last_name or ""):
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} has invalid name fields"
                )
                return False

            # Check for duplicate email (in a real implementation, this would check the database)
            if not await self._is_unique_email(subscriber.email):
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} email already exists: {subscriber.email}"
                )
                return False

            # Validate engagement metrics are non-negative
            if not self._are_valid_engagement_metrics(subscriber):
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} has invalid engagement metrics"
                )
                return False

            self.logger.info(
                f"Subscriber {subscriber.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating subscriber {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email format using regex.

        Args:
            email: Email address to validate

        Returns:
            True if email format is valid
        """
        if not email:
            return False

        # Basic email regex pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, email) is not None

    def _is_allowed_email_domain(self, email: str) -> bool:
        """
        Check if email domain is allowed.

        Args:
            email: Email address to check

        Returns:
            True if domain is allowed
        """
        if not email or "@" not in email:
            return False

        domain = email.split("@")[1].lower()

        # List of blocked domains (spam, temporary email services)
        blocked_domains = {
            "10minutemail.com",
            "tempmail.org",
            "guerrillamail.com",
            "mailinator.com",
            "throwaway.email",
            "temp-mail.org",
        }

        return domain not in blocked_domains

    def _are_valid_names(self, first_name: str, last_name: str) -> bool:
        """
        Validate name fields.

        Args:
            first_name: First name to validate
            last_name: Last name to validate

        Returns:
            True if names are valid
        """
        # Names are optional, but if provided, they should be valid
        for name in [first_name, last_name]:
            if name is not None:
                # Check for minimum length
                if len(name.strip()) == 0:
                    continue  # Empty names are allowed (will be set to None)

                # Check for reasonable length
                if len(name) > 100:
                    return False

                # Check for valid characters (letters, spaces, hyphens, apostrophes)
                if not re.match(r"^[a-zA-Z\s\-']+$", name):
                    return False

        return True

    async def _is_unique_email(self, email: str) -> bool:
        """
        Check if email is unique (not already subscribed).

        Args:
            email: Email address to check

        Returns:
            True if email is unique
        """
        # In a real implementation, this would query the database
        # For now, we'll assume all emails are unique
        # This could be enhanced to use the entity service to search for existing subscribers

        try:
            from common.service.entity_service import SearchConditionRequest
            from services.services import get_entity_service

            entity_service = get_entity_service()

            # Build search condition for email
            builder = SearchConditionRequest.builder()
            builder.equals("email", email)
            condition = builder.build()

            # Search for existing subscribers with this email
            existing_subscribers = await entity_service.search(
                entity_class=Subscriber.ENTITY_NAME,
                condition=condition,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )

            # If any subscribers found, email is not unique
            return len(existing_subscribers) == 0

        except Exception as e:
            self.logger.warning(f"Could not check email uniqueness: {str(e)}")
            # If we can't check, assume it's unique to avoid blocking valid subscriptions
            return True

    def _are_valid_engagement_metrics(self, subscriber: Subscriber) -> bool:
        """
        Validate engagement metrics are non-negative and logical.

        Args:
            subscriber: Subscriber to validate

        Returns:
            True if engagement metrics are valid
        """
        # All counts should be non-negative
        if (
            subscriber.total_emails_sent < 0
            or subscriber.total_emails_opened < 0
            or subscriber.total_emails_clicked < 0
        ):
            return False

        # Opened emails cannot exceed sent emails
        if subscriber.total_emails_opened > subscriber.total_emails_sent:
            return False

        # Clicked emails cannot exceed opened emails
        if subscriber.total_emails_clicked > subscriber.total_emails_opened:
            return False

        return True
