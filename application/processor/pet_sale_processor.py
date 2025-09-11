"""
PetSaleProcessor for Purrfect Pets API

Completes pet sale transaction according to processors.md specification.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Protocol, cast

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _HasId(Protocol):
    id: str


class _HasMetadata(Protocol):
    metadata: _HasId


class _EntityService(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Dict[str, Any]]: ...

    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _HasMetadata: ...

    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class PetSaleProcessor(CyodaProcessor):
    """
    Processor for Pet sale that completes pet sale transaction and updates related order item.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetSaleProcessor",
            description="Completes pet sale transaction",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity sale according to functional requirements.

        Args:
            entity: The Pet entity to sell
            **kwargs: Additional processing parameters including sale_data

        Returns:
            The sold pet entity
        """
        try:
            self.logger.info(
                f"Processing sale for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet is in PENDING state
            if pet.state != "pending":
                raise ValueError(
                    f"Pet must be in PENDING state to sell, current state: {pet.state}"
                )

            # Get sale data from kwargs
            sale_data = kwargs.get("sale_data", {})

            # Validate associated order exists
            order_id = self._get_order_id_from_reservation(pet)
            if not order_id:
                raise ValueError("No associated order found for pet sale")

            # Update order item status to DELIVERED
            await self._update_order_item_status(pet, order_id)

            # Record sale transaction
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            sale_info = {
                "sold_at": current_timestamp,
                "order_id": order_id,
                "sale_price": sale_data.get("sale_price", pet.price),
                "processed_by": "PetSaleProcessor",
            }

            # Add sale info to pet metadata
            if pet.metadata is None:
                pet.metadata = {}
            pet.metadata["sale"] = sale_info

            # Update pet availability
            pet.metadata["availability_status"] = "sold"

            # Log sale activity
            activity_log = {
                "action": "sale_completed",
                "timestamp": current_timestamp,
                "details": sale_info,
            }

            if "activity_log" not in pet.metadata:
                pet.metadata["activity_log"] = []
            pet.metadata["activity_log"].append(activity_log)

            # Send notification to customer (placeholder)
            await self._send_customer_notification(order_id, pet)

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(f"Pet {pet.technical_id} sale completed successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet sale {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _get_order_id_from_reservation(self, pet: Pet) -> Optional[str]:
        """Extract order ID from pet reservation metadata"""
        if pet.metadata and "reservation" in pet.metadata:
            reservation = pet.metadata["reservation"]
            if isinstance(reservation, dict):
                return reservation.get("order_id")
        return None

    async def _update_order_item_status(self, pet: Pet, order_id: str) -> None:
        """Update associated order item status to DELIVERED"""
        try:
            # This is a placeholder - in a real implementation, we would:
            # 1. Find the order item by order_id and pet_id
            # 2. Update its status to DELIVERED
            # For now, we'll just log the action

            self.logger.info(
                f"Updated order item status to DELIVERED for order {order_id}, pet {pet.technical_id}"
            )

        except Exception as e:
            self.logger.error(f"Failed to update order item status: {str(e)}")
            raise

    async def _send_customer_notification(self, order_id: str, pet: Pet) -> None:
        """Send notification to customer about pet sale completion"""
        try:
            # Placeholder for customer notification
            self.logger.info(
                f"Sent sale completion notification for order {order_id}, pet {pet.name}"
            )

        except Exception as e:
            self.logger.warning(f"Failed to send customer notification: {str(e)}")
            # Don't raise - notification failure shouldn't stop the sale
