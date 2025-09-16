"""Order Validation Criterion for Purrfect Pets API."""

import logging
from typing import Any, Dict, Optional

from application.entity.order.version_1.order import Order
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OrderValidationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate order can be confirmed."""

    def __init__(self):
        super().__init__(
            name="OrderValidationCriterion",
            description="Validate order can be confirmed",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if order can be confirmed."""
        try:
            if not isinstance(entity, Order):
                raise CriteriaError(self.name, "Entity must be an Order instance")

            # Check if order state is PLACED
            if entity.state != "placed":
                logger.debug(
                    f"Order {entity.entity_id} is not placed, current state: {entity.state}"
                )
                return False

            # Check if total amount is positive
            if entity.totalAmount <= 0:
                logger.debug(
                    f"Order {entity.entity_id} has invalid total amount: {entity.totalAmount}"
                )
                return False

            # TODO: In a real implementation, this would:
            # 1. Check if pet is still available using EntityService
            # 2. Validate owner is active using EntityService
            # 3. Validate payment method is valid

            # Get pet and owner information from kwargs
            pet = kwargs.get("pet")
            owner = kwargs.get("owner")
            payment_method = kwargs.get("payment_method")

            # Check pet availability (if provided)
            if pet:
                if hasattr(pet, "state") and pet.state not in ["available", "pending"]:
                    logger.debug(
                        f"Pet {pet.entity_id} is not available, current state: {pet.state}"
                    )
                    return False

                if hasattr(pet, "id") and entity.petId != pet.id:
                    logger.debug(
                        f"Order pet ID {entity.petId} does not match provided pet {pet.id}"
                    )
                    return False

            # Check owner status (if provided)
            if owner:
                if hasattr(owner, "state") and owner.state != "active":
                    logger.debug(
                        f"Owner {owner.entity_id} is not active, current state: {owner.state}"
                    )
                    return False

                if hasattr(owner, "id") and entity.ownerId != owner.id:
                    logger.debug(
                        f"Order owner ID {entity.ownerId} does not match provided owner {owner.id}"
                    )
                    return False

            # Check payment method (if provided)
            if payment_method:
                valid_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]
                if payment_method not in valid_methods:
                    logger.debug(f"Invalid payment method: {payment_method}")
                    return False

            logger.debug(f"Order {entity.entity_id} can be confirmed")
            return True

        except Exception as e:
            logger.exception(
                f"Failed to check validation criteria for order {entity.entity_id}"
            )
            raise CriteriaError(
                self.name, f"Failed to check order validation: {str(e)}", e
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Order) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Order"
        )
