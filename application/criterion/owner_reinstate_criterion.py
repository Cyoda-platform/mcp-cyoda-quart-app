"""Owner Reinstate Criterion for Purrfect Pets API."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OwnerReinstateCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate if suspended owner can be reinstated."""

    def __init__(self):
        super().__init__(
            name="OwnerReinstateCriterion",
            description="Check if suspended owner can be reinstated",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if owner can be reinstated."""
        try:
            if not isinstance(entity, Owner):
                raise CriteriaError(self.name, "Entity must be an Owner instance")

            # Check if owner state is SUSPENDED
            if entity.state != "suspended":
                logger.debug(
                    f"Owner {entity.entity_id} is not suspended, current state: {entity.state}"
                )
                return False

            # Check if suspension period is complete
            suspended_at = entity.get_metadata("suspended_at")
            if not suspended_at:
                logger.debug(f"No suspension date found for owner {entity.entity_id}")
                return False

            try:
                suspension_date = datetime.fromisoformat(
                    suspended_at.replace("Z", "+00:00")
                )
                current_date = datetime.now(timezone.utc)

                # Default suspension period is 30 days
                suspension_period_days = kwargs.get("suspension_period_days", 30)
                suspension_end_date = suspension_date + timedelta(
                    days=suspension_period_days
                )

                if current_date < suspension_end_date:
                    logger.debug(
                        f"Suspension period not complete for owner {entity.entity_id}"
                    )
                    return False

            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Invalid suspension date format for owner {entity.entity_id}: {e}"
                )
                return False

            # TODO: In a real implementation, this would:
            # 1. Check if reinstatement conditions are met
            # 2. Validate any required actions have been completed
            # 3. Check for any new violations during suspension

            # Check if reinstatement conditions are met (from metadata)
            conditions_met = entity.get_metadata("reinstatement_conditions_met", False)
            if not conditions_met:
                # Allow reinstatement if no specific conditions are set
                conditions_met = entity.get_metadata("reinstatement_conditions") is None

            if not conditions_met:
                logger.debug(
                    f"Reinstatement conditions not met for owner {entity.entity_id}"
                )
                return False

            # Check for new violations during suspension
            new_violations = entity.get_metadata("violations_during_suspension", [])
            if new_violations:
                logger.debug(
                    f"Owner {entity.entity_id} has new violations during suspension: {new_violations}"
                )
                return False

            logger.debug(f"Owner {entity.entity_id} can be reinstated")
            return True

        except Exception as e:
            logger.exception(
                f"Failed to check reinstate criteria for owner {entity.entity_id}"
            )
            raise CriteriaError(
                self.name, f"Failed to check owner reinstatement: {str(e)}", e
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Owner"
        )
