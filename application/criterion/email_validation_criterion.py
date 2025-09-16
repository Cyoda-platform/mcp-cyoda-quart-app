"""
Email Validation Criterion for validating email format and domain.
"""

import logging
import re
from typing import Any, Dict, Optional

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class EmailValidationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate email format and domain."""

    def __init__(self, name: str = "EmailValidationCriterion", description: str = ""):
        super().__init__(
            name=name, description=description or "Validates email format and domain"
        )

        # Email regex pattern
        self.email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )

        # Blocked domains list (example)
        self.blocked_domains = {
            "tempmail.com",
            "throwaway.email",
            "10minutemail.com",
            "guerrillamail.com",
            "mailinator.com",
        }

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if email is valid."""
        try:
            if not isinstance(entity, Subscriber):
                return False

            email = entity.email

            # Check if email is null or empty
            if not email:
                return False

            # Check email format with regex
            if not self.email_pattern.match(email):
                return False

            # Extract domain
            domain = self._extract_domain(email)
            if not domain:
                return False

            # Check if domain exists (simplified check)
            if not self._domain_exists(domain):
                return False

            # Check if domain is blocked
            if domain.lower() in self.blocked_domains:
                return False

            return True

        except Exception as e:
            logger.exception(
                f"Failed to validate email for subscriber {entity.entity_id}"
            )
            raise CriteriaError(self.name, f"Failed to validate email: {str(e)}", e)

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Subscriber)

    def _extract_domain(self, email: str) -> Optional[str]:
        """Extract domain from email address."""
        try:
            return email.split("@")[1]
        except (IndexError, AttributeError):
            return None

    def _domain_exists(self, domain: str) -> bool:
        """Check if domain exists (simplified implementation)."""
        # In real implementation, perform DNS lookup
        # For now, assume domain exists if it has proper format
        return "." in domain and len(domain) > 3
