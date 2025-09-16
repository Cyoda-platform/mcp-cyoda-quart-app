"""Category Archive Criterion for Purrfect Pets API."""

import logging
from typing import Any, Dict, Optional

from application.entity.category.version_1.category import Category
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class CategoryArchiveCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate if category can be archived."""

    def __init__(self):
        super().__init__(
            name="CategoryArchiveCriterion",
            description="Check if category can be archived",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if category can be archived."""
        try:
            if not isinstance(entity, Category):
                raise CriteriaError(self.name, "Entity must be a Category instance")

            # Check if category state is INACTIVE
            if entity.state != "inactive":
                logger.debug(
                    f"Category {entity.entity_id} is not inactive, current state: {entity.state}"
                )
                return False

            # TODO: In a real implementation, this would:
            # 1. Check if category has no active pets using EntityService
            # 2. Check if category has no pending orders using EntityService

            # Check if category has active pets (from kwargs or metadata)
            active_pets_count = kwargs.get("active_pets_count", 0)
            if active_pets_count > 0:
                logger.debug(
                    f"Category {entity.entity_id} has {active_pets_count} active pets"
                )
                return False

            # Check if category has pending orders (from kwargs or metadata)
            pending_orders_count = kwargs.get("pending_orders_count", 0)
            if pending_orders_count > 0:
                logger.debug(
                    f"Category {entity.entity_id} has {pending_orders_count} pending orders"
                )
                return False

            # Check metadata for validation flags
            pets_validated = entity.get_metadata("pets_validated", False)
            orders_validated = entity.get_metadata("orders_validated", False)

            # If validation hasn't been done, assume it's safe to archive
            # In a real implementation, this would trigger the validation
            if not pets_validated or not orders_validated:
                logger.debug(f"Category {entity.entity_id} validation not complete")
                # For now, we'll allow archiving if no explicit counts are provided
                if (
                    "active_pets_count" not in kwargs
                    and "pending_orders_count" not in kwargs
                ):
                    logger.debug(
                        f"No pet/order counts provided, allowing archive for category {entity.entity_id}"
                    )
                    return True
                return False

            # Check if category has been inactive for sufficient time
            deactivated_at = entity.get_metadata("deactivated_at")
            if deactivated_at:
                try:
                    from datetime import datetime, timedelta, timezone

                    deactivation_date = datetime.fromisoformat(
                        deactivated_at.replace("Z", "+00:00")
                    )
                    current_date = datetime.now(timezone.utc)

                    # Require category to be inactive for at least 30 days before archiving
                    min_inactive_days = kwargs.get("min_inactive_days", 30)
                    min_inactive_period = timedelta(days=min_inactive_days)

                    if current_date - deactivation_date < min_inactive_period:
                        logger.debug(
                            f"Category {entity.entity_id} has not been inactive long enough"
                        )
                        return False

                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"Invalid deactivation date format for category {entity.entity_id}: {e}"
                    )

            logger.debug(f"Category {entity.entity_id} can be archived")
            return True

        except Exception as e:
            logger.exception(
                f"Failed to check archive criteria for category {entity.entity_id}"
            )
            raise CriteriaError(
                self.name, f"Failed to check category archive: {str(e)}", e
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Category) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Category"
        )
