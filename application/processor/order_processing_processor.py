"""
OrderProcessingProcessor for Purrfect Pets Application

Begins processing the order as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.order.version_1.order import Order
from services.services import get_entity_service


class OrderProcessingProcessor(CyodaProcessor):
    """
    Processor for beginning Order processing.
    Validates pet is still reserved and prepares for delivery.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderProcessingProcessor",
            description="Begin processing the order"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity for processing stage.

        Args:
            entity: The Order entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processing Order entity
        """
        try:
            self.logger.info(
                f"Processing Order processing for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Validate pet is still reserved
            entity_service = get_entity_service()
            try:
                pet_response = await entity_service.get_by_id(
                    entity_id=str(order.pet_id),
                    entity_class="Pet",
                    entity_version="1"
                )
                if not pet_response:
                    raise ValueError(f"Pet with ID {order.pet_id} not found")
                
                pet_state = getattr(pet_response.metadata, 'state', None)
                if pet_state != "pending":
                    raise ValueError(f"Pet must be in pending state for processing, current state: {pet_state}")
                    
            except Exception as e:
                self.logger.error(f"Pet validation failed: {str(e)}")
                raise ValueError(f"Pet validation failed: {str(e)}")

            # Prepare pet for delivery (health check, grooming if needed)
            self._prepare_pet_for_delivery(order)

            # Validate delivery address
            if not order.delivery_address:
                raise ValueError("Delivery address is required for order processing")

            # Assign order to fulfillment team
            fulfillment_data = kwargs.get('fulfillment_data', {})
            assigned_to = fulfillment_data.get('assigned_to', 'default-fulfillment-team')
            
            # Add fulfillment information to order metadata
            if not hasattr(order, 'metadata') or order.metadata is None:
                order.metadata = {}
            order.metadata['assigned_to'] = assigned_to
            order.metadata['processing_started_at'] = order.updated_at

            # Set updated timestamp
            order.update_timestamp()

            # Send processing notification to customer
            self._send_processing_notification(order)

            self.logger.info(f"Order processing processed successfully for {order.technical_id}")
            return order

        except Exception as e:
            self.logger.error(
                f"Error processing Order processing for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _prepare_pet_for_delivery(self, order: Order) -> None:
        """
        Prepare pet for delivery (health check, grooming if needed).
        
        Args:
            order: The order being processed
        """
        try:
            self.logger.info(f"Preparing Pet {order.pet_id} for delivery")
            
            # Simulate pet preparation activities
            # In a real implementation, this might involve:
            # - Health check verification
            # - Grooming appointment
            # - Vaccination record update
            # - Microchip verification
            
            self.logger.info(f"Pet {order.pet_id} prepared for delivery")
            
        except Exception as e:
            self.logger.warning(f"Pet preparation warning: {str(e)}")

    def _send_processing_notification(self, order: Order) -> None:
        """
        Send processing notification to customer.
        
        Args:
            order: The order being processed
        """
        try:
            self.logger.info(f"Sending processing notification for Order {order.technical_id} to User {order.user_id}")
            # In a real implementation, this would send an actual notification
            
        except Exception as e:
            self.logger.warning(f"Failed to send processing notification: {str(e)}")
