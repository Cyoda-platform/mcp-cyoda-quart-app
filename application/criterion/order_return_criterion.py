"""Order Return Criterion for Purrfect Pets API."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderReturnCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate if order can be returned."""

    def __init__(self):
        super().__init__(
            name="OrderReturnCriterion", description="Check if order can be returned"
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if order can be returned."""
        try:
            if not isinstance(entity, Order):
                raise CriteriaError(self.name, "Entity must be an Order instance")

            # Check if order state is DELIVERED
            if entity.state != "delivered":
                logger.debug(
                    f"Order {entity.entity_id} is not delivered, current state: {entity.state}"
                )
                return False

            # Check if return is within return period
            delivered_at = entity.get_metadata("delivered_at")
            if not delivered_at:
                logger.debug(f"No delivery date found for order {entity.entity_id}")
                return False

            try:
                delivery_date = datetime.fromisoformat(
                    delivered_at.replace("Z", "+00:00")
                )
                current_date = datetime.now(timezone.utc)

                # Default return period is 14 days
                return_period_days = kwargs.get("return_period_days", 14)
                return_deadline = delivery_date + timedelta(days=return_period_days)

                if current_date > return_deadline:
                    logger.debug(f"Return period expired for order {entity.entity_id}")
                    return False

            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Invalid delivery date format for order {entity.entity_id}: {e}"
                )
                return False

            # Get return reason from kwargs
            return_reason = kwargs.get("returnReason") or kwargs.get("return_reason")

            if not return_reason:
                logger.debug(f"No return reason provided for order {entity.entity_id}")
                return False

            # Validate return reason
            valid_reasons = [
                "defective_pet",
                "not_as_described",
                "health_issues",
                "allergic_reaction",
                "changed_mind",
                "family_circumstances",
                "pet_behavior_issues",
            ]

            if return_reason not in valid_reasons:
                logger.debug(
                    f"Invalid return reason '{return_reason}' for order {entity.entity_id}"
                )
                return False

            # TODO: In a real implementation, this would:
            # 1. Check if pet is in returnable condition
            # 2. Validate return policy based on reason
            # 3. Check for any restrictions or special conditions

            # Check if pet is in returnable condition (from kwargs)
            pet_condition = kwargs.get("pet_condition", "good")
            returnable_conditions = ["good", "excellent", "minor_issues"]

            if pet_condition not in returnable_conditions:
                logger.debug(f"Pet condition '{pet_condition}' not suitable for return")
                return False

            # Check return policy based on reason
            if return_reason == "changed_mind":
                # Changed mind returns might have stricter conditions
                return_period_for_changed_mind = kwargs.get(
                    "changed_mind_return_days", 7
                )
                changed_mind_deadline = delivery_date + timedelta(
                    days=return_period_for_changed_mind
                )

                if current_date > changed_mind_deadline:
                    logger.debug(
                        f"Changed mind return period expired for order {entity.entity_id}"
                    )
                    return False

            logger.debug(
                f"Order {entity.entity_id} can be returned for reason: {return_reason}"
            )
            return True

        except Exception as e:
            logger.exception(
                f"Failed to check return criteria for order {entity.entity_id}"
            )
            raise CriteriaError(self.name, f"Failed to check order return: {str(e)}", e)

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
