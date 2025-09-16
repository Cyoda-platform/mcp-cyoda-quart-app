"""Owner Suspension Criterion for Purrfect Pets API."""

import logging
from typing import Any, Dict, Optional

from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OwnerSuspensionCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate if owner should be suspended."""

    def __init__(self):
        super().__init__(
            name="OwnerSuspensionCriterion",
            description="Check if owner should be suspended",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if owner should be suspended."""
        try:
            if not isinstance(entity, Owner):
                raise CriteriaError(self.name, "Entity must be an Owner instance")

            # Check if owner state is ACTIVE
            if entity.state != "active":
                logger.debug(
                    f"Owner {entity.entity_id} is not active, current state: {entity.state}"
                )
                return False

            # Get suspension reason from kwargs
            suspension_reason = kwargs.get("suspensionReason") or kwargs.get(
                "suspension_reason"
            )

            if not suspension_reason:
                logger.debug(
                    f"No suspension reason provided for owner {entity.entity_id}"
                )
                return False

            # Validate suspension reason is valid
            valid_reasons = [
                "policy_violation",
                "fraudulent_activity",
                "payment_issues",
                "abuse_reports",
                "terms_violation",
                "security_concerns",
            ]

            if suspension_reason not in valid_reasons:
                logger.debug(
                    f"Invalid suspension reason '{suspension_reason}' for owner {entity.entity_id}"
                )
                return False

            # TODO: In a real implementation, this would:
            # 1. Check if suspension is justified based on the reason
            # 2. Validate evidence or documentation for suspension
            # 3. Check suspension policies and procedures

            # Check if suspension is justified (simplified validation)
            justification = kwargs.get("justification")
            if not justification:
                logger.debug(
                    f"No justification provided for suspending owner {entity.entity_id}"
                )
                return False

            logger.debug(
                f"Owner {entity.entity_id} can be suspended for reason: {suspension_reason}"
            )
            return True

        except Exception as e:
            logger.exception(
                f"Failed to check suspension criteria for owner {entity.entity_id}"
            )
            raise CriteriaError(
                self.name, f"Failed to check owner suspension: {str(e)}", e
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Owner"
        )
