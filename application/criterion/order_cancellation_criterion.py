"""Order Cancellation Criterion for Purrfect Pets API."""
import logging
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from application.entity.order.version_1.order import Order

logger = logging.getLogger(__name__)


class OrderCancellationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate if order can be cancelled."""
    
    def __init__(self):
        super().__init__(
            name="OrderCancellationCriterion",
            description="Check if order can be cancelled"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if order can be cancelled."""
        try:
            if not isinstance(entity, Order):
                raise CriteriaError(self.name, "Entity must be an Order instance")
            
            # Check if order state allows cancellation
            cancellable_states = ["placed", "confirmed"]
            if entity.state not in cancellable_states:
                logger.debug(f"Order {entity.entity_id} cannot be cancelled, current state: {entity.state}")
                return False
            
            # Get cancellation reason from kwargs
            cancellation_reason = kwargs.get("cancellationReason") or kwargs.get("cancellation_reason")
            
            if not cancellation_reason:
                logger.debug(f"No cancellation reason provided for order {entity.entity_id}")
                return False
            
            # Validate cancellation reason
            valid_reasons = [
                "customer_request",
                "payment_failed",
                "pet_unavailable",
                "address_invalid",
                "fraud_detected",
                "system_error"
            ]
            
            if cancellation_reason not in valid_reasons:
                logger.debug(f"Invalid cancellation reason '{cancellation_reason}' for order {entity.entity_id}")
                return False
            
            # TODO: In a real implementation, this would:
            # 1. Check cancellation policy based on order state and timing
            # 2. Validate business rules for cancellation
            # 3. Check if refund is possible
            
            # Check cancellation policy (simplified)
            cancellation_policy = kwargs.get("cancellation_policy", "standard")
            
            if cancellation_policy == "strict" and entity.state == "confirmed":
                # In strict policy, confirmed orders might not be cancellable
                logger.debug(f"Order {entity.entity_id} cannot be cancelled due to strict policy")
                return False
            
            # Check if cancellation is allowed based on timing (from metadata)
            order_age_hours = kwargs.get("order_age_hours", 0)
            max_cancellation_hours = kwargs.get("max_cancellation_hours", 24)
            
            if order_age_hours > max_cancellation_hours:
                logger.debug(f"Order {entity.entity_id} is too old for cancellation: {order_age_hours} hours")
                return False
            
            logger.debug(f"Order {entity.entity_id} can be cancelled for reason: {cancellation_reason}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check cancellation criteria for order {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check order cancellation: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Order"
        )
