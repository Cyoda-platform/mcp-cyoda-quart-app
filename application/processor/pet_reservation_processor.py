"""
PetReservationProcessor for Purrfect Pets Application

Reserves pet for a pending order as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from application.entity.order.version_1.order import Order
from services.services import get_entity_service


class PetReservationProcessor(CyodaProcessor):
    """
    Processor for reserving Pet entities for pending orders.
    Creates new order entity and triggers order workflow.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationProcessor",
            description="Reserve pet for a pending order"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for reservation.

        Args:
            entity: The Pet entity to reserve
            **kwargs: Additional processing parameters including order data

        Returns:
            The reserved Pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet reservation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Extract order data from kwargs
            order_data = kwargs.get('order_data', {})
            user_id = order_data.get('user_id') or order_data.get('userId')
            quantity = order_data.get('quantity', 1)
            delivery_address = order_data.get('delivery_address') or order_data.get('deliveryAddress')
            special_instructions = order_data.get('special_instructions') or order_data.get('specialInstructions')
            payment_method = order_data.get('payment_method') or order_data.get('paymentMethod')

            # Validate order information is complete
            if not user_id:
                raise ValueError("User ID is required for reservation")

            # Validate user exists and is active
            entity_service = get_entity_service()
            try:
                user_response = await entity_service.get_by_id(
                    entity_id=str(user_id),
                    entity_class="User",
                    entity_version="1"
                )
                if not user_response:
                    raise ValueError(f"User with ID {user_id} not found")
                
                user_state = getattr(user_response.metadata, 'state', None)
                if user_state not in ["active", "verified"]:
                    raise ValueError(f"User must be active or verified, current state: {user_state}")
                    
            except Exception as e:
                self.logger.error(f"User validation failed: {str(e)}")
                raise ValueError(f"Invalid user: {str(e)}")

            # Create new order entity
            try:
                # Calculate total amount based on pet price and quantity
                total_amount = pet.price * quantity if pet.price else None

                # Create order data
                order_entity_data = {
                    "userId": user_id,
                    "petId": int(pet.technical_id) if pet.technical_id and pet.technical_id.isdigit() else None,
                    "quantity": quantity,
                    "totalAmount": float(total_amount) if total_amount else None,
                    "deliveryAddress": delivery_address,
                    "specialInstructions": special_instructions,
                    "paymentMethod": payment_method
                }

                # Remove None values
                order_entity_data = {k: v for k, v in order_entity_data.items() if v is not None}

                # Save the new order entity
                order_response = await entity_service.save(
                    entity=order_entity_data,
                    entity_class="Order",
                    entity_version="1"
                )

                created_order_id = order_response.metadata.id
                self.logger.info(f"Created Order {created_order_id} for Pet {pet.technical_id}")

                # Trigger order workflow transition to CONFIRMED if payment method is provided
                if payment_method:
                    try:
                        await entity_service.execute_transition(
                            entity_id=created_order_id,
                            transition="transition_to_order_confirmed",
                            entity_class="Order",
                            entity_version="1"
                        )
                        self.logger.info(f"Order {created_order_id} transitioned to confirmed")
                    except Exception as e:
                        self.logger.warning(f"Could not confirm order {created_order_id}: {str(e)}")

            except Exception as e:
                self.logger.error(f"Failed to create order for Pet {pet.technical_id}: {str(e)}")
                raise ValueError(f"Failed to create order: {str(e)}")

            # Set pet updated timestamp
            pet.update_timestamp()

            self.logger.info(f"Pet reservation processed successfully for {pet.technical_id}")
            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet reservation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
