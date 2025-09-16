"""Order Shipping Criterion for Purrfect Pets API."""
import logging
from typing import Optional, Dict, Any

from entity.cyoda_entity import CyodaEntity
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from application.entity.order.version_1.order import Order

logger = logging.getLogger(__name__)


class OrderShippingCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate if order is ready for shipping."""
    
    def __init__(self):
        super().__init__(
            name="OrderShippingCriterion",
            description="Check if order is ready for shipping"
        )
    
    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if order is ready for shipping."""
        try:
            if not isinstance(entity, Order):
                raise CriteriaError(self.name, "Entity must be an Order instance")
            
            # Check if order state is PREPARING
            if entity.state != "preparing":
                logger.debug(f"Order {entity.entity_id} is not preparing, current state: {entity.state}")
                return False
            
            # Check if delivery address is valid
            if not entity.deliveryAddress or not entity.deliveryAddress.strip():
                logger.debug(f"Order {entity.entity_id} has no delivery address")
                return False
            
            # TODO: In a real implementation, this would:
            # 1. Check if pet documentation is complete
            # 2. Validate delivery address is valid and reachable
            # 3. Check if shipping method is available
            
            # Check if pet documentation is complete (from metadata)
            documentation_complete = entity.get_metadata("documentation_prepared", False)
            if not documentation_complete:
                logger.debug(f"Order {entity.entity_id} documentation is not complete")
                return False
            
            # Check if delivery address is valid (basic validation)
            address_parts = entity.deliveryAddress.split(',')
            if len(address_parts) < 2:
                logger.debug(f"Order {entity.entity_id} has invalid delivery address format")
                return False
            
            # Check if shipping method is available (from kwargs or metadata)
            shipping_method = kwargs.get("shipping_method") or entity.get_metadata("shipping_method", "standard")
            available_methods = ["standard", "express", "overnight", "pickup"]
            
            if shipping_method not in available_methods:
                logger.debug(f"Order {entity.entity_id} has invalid shipping method: {shipping_method}")
                return False
            
            # Check if preparation is complete (from metadata)
            preparation_complete = entity.get_metadata("preparation_started")
            if not preparation_complete:
                logger.debug(f"Order {entity.entity_id} preparation has not started")
                return False
            
            logger.debug(f"Order {entity.entity_id} is ready for shipping")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to check shipping criteria for order {entity.entity_id}")
            raise CriteriaError(self.name, f"Failed to check order shipping: {str(e)}", e)
    
    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, 'ENTITY_NAME') and entity.ENTITY_NAME == "Order"
        )
