"""
OrderValidationCriterion for Purrfect Pets API

Validates order before approval according to criteria.md specification.
"""

from typing import Any, Dict, Optional, Protocol, cast

from application.entity.order.version_1.order import Order
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class _EntityService(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Dict[str, Any]]: ...


class OrderValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Order that validates order before approval.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderValidationCriterion",
            description="Validates order before approval",
        )
        self.entity_service: Optional[_EntityService] = None

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the order is valid for approval.

        Args:
            entity: The CyodaEntity to validate (expected to be Order)
            **kwargs: Additional criteria parameters

        Returns:
            True if order is valid for approval, False otherwise
        """
        try:
            self.logger.info(
                f"Validating order {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Check if order state is PLACED
            if order.state != "placed":
                self.logger.warning(
                    f"Order {order.technical_id} is not in PLACED state, current state: {order.state}"
                )
                return False

            # Check if order userId is not null
            if not order.user_id:
                self.logger.warning(f"Order {order.technical_id} has no user ID")
                return False

            # Check if user associated with order is ACTIVE
            if not await self._validate_user_active(order.user_id):
                return False

            # Check if order has items
            if not order.metadata or "order_items" not in order.metadata:
                self.logger.warning(f"Order {order.technical_id} has no items")
                return False

            order_items = order.metadata["order_items"]
            if not order_items or len(order_items) == 0:
                self.logger.warning(f"Order {order.technical_id} has empty items list")
                return False

            # Check if all associated pets are available
            for item in order_items:
                pet_id = item.get("pet_id")
                if pet_id and not await self._validate_pet_available(pet_id):
                    return False

            # Check if payment information is valid
            if not await self._validate_payment_information(order):
                return False

            self.logger.info(f"Order {order.technical_id} passed validation check")
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating order {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _validate_user_active(self, user_id: int) -> bool:
        """Validate user is active"""
        try:
            entity_service = self._get_entity_service()
            user_data = await entity_service.get_by_id(
                entity_id=str(user_id), entity_class="User", entity_version="1"
            )

            if not user_data:
                self.logger.warning(f"User {user_id} not found")
                return False

            if user_data.get("state") != "active":
                self.logger.warning(f"User {user_id} is not active")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating user {user_id}: {str(e)}")
            return False

    async def _validate_pet_available(self, pet_id: int) -> bool:
        """Validate pet is available"""
        try:
            entity_service = self._get_entity_service()
            pet_data = await entity_service.get_by_id(
                entity_id=str(pet_id), entity_class="Pet", entity_version="1"
            )

            if not pet_data:
                self.logger.warning(f"Pet {pet_id} not found")
                return False

            if pet_data.get("state") not in ["available", "pending"]:
                self.logger.warning(f"Pet {pet_id} is not available")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating pet {pet_id}: {str(e)}")
            return False

    async def _validate_payment_information(self, order: Order) -> bool:
        """Validate payment information"""
        if not order.payment_method:
            self.logger.warning(f"Order {order.technical_id} has no payment method")
            return False

        if not order.total_amount or order.total_amount <= 0:
            self.logger.warning(f"Order {order.technical_id} has invalid total amount")
            return False

        return True
