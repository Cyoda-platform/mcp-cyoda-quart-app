"""
PetReleaseProcessor for Purrfect Pets Application

Releases pet from pending status back to available as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service


class PetReleaseProcessor(CyodaProcessor):
    """
    Processor for releasing Pet entities from pending status.
    Cancels associated orders and makes pet available again.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReleaseProcessor",
            description="Release pet from pending status back to available"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for release from pending status.

        Args:
            entity: The Pet entity to release
            **kwargs: Additional processing parameters

        Returns:
            The released Pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet release for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Find associated pending order
            entity_service = get_entity_service()
            try:
                # Search for orders with this pet ID
                from common.service.entity_service import SearchConditionRequest
                
                builder = SearchConditionRequest.builder()
                builder.equals("petId", str(pet.technical_id))
                search_condition = builder.build()

                order_results = await entity_service.search(
                    entity_class="Order",
                    condition=search_condition,
                    entity_version="1"
                )

                # Find orders in states that should be cancelled
                orders_to_cancel = []
                for order_result in order_results:
                    order_state = getattr(order_result.metadata, 'state', None)
                    if order_state in ["placed", "confirmed"]:
                        orders_to_cancel.append(order_result)

                # Cancel the orders
                for order in orders_to_cancel:
                    try:
                        await entity_service.execute_transition(
                            entity_id=order.metadata.id,
                            transition="transition_to_order_cancelled",
                            entity_class="Order",
                            entity_version="1"
                        )
                        self.logger.info(f"Order {order.metadata.id} cancelled during pet release")
                    except Exception as e:
                        self.logger.error(f"Failed to cancel order {order.metadata.id}: {str(e)}")
                        # Continue with other orders

                if orders_to_cancel:
                    self.logger.info(f"Cancelled {len(orders_to_cancel)} orders for Pet {pet.technical_id}")
                else:
                    self.logger.info(f"No orders found to cancel for Pet {pet.technical_id}")

            except Exception as e:
                self.logger.error(f"Failed to find or cancel associated orders: {str(e)}")
                # Continue processing - order cancellation failure shouldn't prevent pet release

            # Clear any reservation data (if we had specific reservation fields)
            # For now, we just update the timestamp

            # Set pet updated timestamp
            pet.update_timestamp()

            self.logger.info(f"Pet release processed successfully for {pet.technical_id}")
            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet release for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
