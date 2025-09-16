"""
OrderCreationProcessor for Purrfect Pets Application

Initializes a new order record as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.order.version_1.order import Order
from services.services import get_entity_service


class OrderCreationProcessor(CyodaProcessor):
    """
    Processor for initializing new Order entities.
    Validates required fields and calculates total amount.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderCreationProcessor",
            description="Initialize a new order record"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity during creation.

        Args:
            entity: The Order entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed Order entity with initialized data
        """
        try:
            self.logger.info(
                f"Processing Order creation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Validate required fields
            if not order.user_id or order.user_id <= 0:
                raise ValueError("Valid user ID is required")
            
            if not order.pet_id or order.pet_id <= 0:
                raise ValueError("Valid pet ID is required")

            # Validate user exists and is active
            entity_service = get_entity_service()
            try:
                user_response = await entity_service.get_by_id(
                    entity_id=str(order.user_id),
                    entity_class="User",
                    entity_version="1"
                )
                if not user_response:
                    raise ValueError(f"User with ID {order.user_id} not found")
                
                user_state = getattr(user_response.metadata, 'state', None)
                if user_state not in ["active", "verified"]:
                    raise ValueError(f"User must be active or verified, current state: {user_state}")
                    
            except Exception as e:
                self.logger.error(f"User validation failed: {str(e)}")
                raise ValueError(f"Invalid user: {str(e)}")

            # Validate pet exists and is available
            try:
                pet_response = await entity_service.get_by_id(
                    entity_id=str(order.pet_id),
                    entity_class="Pet",
                    entity_version="1"
                )
                if not pet_response:
                    raise ValueError(f"Pet with ID {order.pet_id} not found")
                
                pet_state = getattr(pet_response.metadata, 'state', None)
                if pet_state != "available":
                    raise ValueError(f"Pet must be available for order, current state: {pet_state}")
                
                # Get pet data for price calculation
                pet_data = pet_response.data
                pet_price = None
                if hasattr(pet_data, 'price'):
                    pet_price = pet_data.price
                elif isinstance(pet_data, dict):
                    pet_price = pet_data.get('price')
                
                if pet_price is not None:
                    pet_price = Decimal(str(pet_price))
                    
            except Exception as e:
                self.logger.error(f"Pet validation failed: {str(e)}")
                raise ValueError(f"Invalid pet: {str(e)}")

            # Calculate total amount based on pet price and quantity
            if order.quantity is None:
                order.quantity = 1
                
            if pet_price is not None and order.total_amount is None:
                order.total_amount = pet_price * order.quantity

            # Set order date to current timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            order.order_date = current_time
            order.created_at = current_time
            order.updated_at = current_time

            self.logger.info(f"Order creation processed successfully for {order.technical_id}")
            return order

        except Exception as e:
            self.logger.error(
                f"Error processing Order creation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
