"""
EmailDelivery Failure Criterion for checking if email delivery failed.
"""

import logging
from typing import Any, Dict, Optional

from application.entity.emaildelivery.version_1.emaildelivery import \
    EmailDelivery
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class EmailDeliveryFailureCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if email delivery failed."""

    def __init__(
        self, name: str = "EmailDeliveryFailureCriterion", description: str = ""
    ):
        super().__init__(
            name=name, description=description or "Checks if email delivery failed"
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if email delivery failed."""
        try:
            if not isinstance(entity, EmailDelivery):
                return False

            # Check if there's an error message
            if entity.errorMessage:
                return True

            # Check delivery status with email service provider
            delivery_status = self._check_delivery_status_with_provider(entity)
            if delivery_status in ["failed", "rejected", "bounced"]:
                return True

            # Check if delivery attempts were made but no sent date
            if entity.deliveryAttempts > 0 and not entity.sentDate:
                return True

            return False

        except Exception as e:
            logger.exception(
                f"Failed to check failure criteria for email delivery {entity.entity_id}"
            )
            raise CriteriaError(
                self.name, f"Failed to check failure criteria: {str(e)}", e
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, EmailDelivery)

    def _check_delivery_status_with_provider(self, entity: EmailDelivery) -> str:
        """Check delivery status with email service provider (simulated)."""
        # In real implementation, integrate with actual email service provider
        if entity.errorMessage:
            return "failed"
        elif entity.sentDate:
            return "delivered"
        return "pending"
