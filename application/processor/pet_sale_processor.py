"""
PetSaleProcessor for Purrfect Pets Application

Completes the sale of a pet as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service


class PetSaleProcessor(CyodaProcessor):
    """
    Processor for completing Pet sales.
    Updates associated order and handles payment confirmation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetSaleProcessor",
            description="Complete the sale of a pet"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for sale completion.

        Args:
            entity: The Pet entity to mark as sold
            **kwargs: Additional processing parameters including payment data

        Returns:
            The sold Pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet sale for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Extract payment data from kwargs
            payment_data = kwargs.get('payment_data', {})
            payment_confirmation = payment_data.get('payment_confirmation') or payment_data.get('paymentConfirmation')

            # Validate payment is completed
            if not payment_confirmation:
                raise ValueError("Payment confirmation is required to complete sale")

            # Find associated pending order
            entity_service = get_entity_service()
            try:
                # Search for orders with this pet ID in pending states
                from common.service.entity_service import SearchConditionRequest
                
                builder = SearchConditionRequest.builder()
                builder.equals("petId", str(pet.technical_id))
                search_condition = builder.build()

                order_results = await entity_service.search(
                    entity_class="Order",
                    condition=search_condition,
                    entity_version="1"
                )

                # Find the most recent order in confirmed state
                associated_order = None
                for order_result in order_results:
                    order_state = getattr(order_result.metadata, 'state', None)
                    if order_state == "confirmed":
                        associated_order = order_result
                        break

                if not associated_order:
                    raise ValueError("No confirmed order found for this pet")

                # Update associated order to PROCESSING state
                try:
                    await entity_service.execute_transition(
                        entity_id=associated_order.metadata.id,
                        transition="transition_to_order_processing",
                        entity_class="Order",
                        entity_version="1"
                    )
                    self.logger.info(f"Order {associated_order.metadata.id} transitioned to processing")
                except Exception as e:
                    self.logger.error(f"Failed to transition order to processing: {str(e)}")
                    raise ValueError(f"Failed to update order status: {str(e)}")

            except Exception as e:
                self.logger.error(f"Failed to find or update associated order: {str(e)}")
                raise ValueError(f"Order processing failed: {str(e)}")

            # Set pet sale date and update timestamp
            pet.update_timestamp()

            # Send confirmation email to customer (simulated)
            self.logger.info(f"Sale confirmation email would be sent for Pet {pet.technical_id}")

            self.logger.info(f"Pet sale processed successfully for {pet.technical_id}")
            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet sale for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
