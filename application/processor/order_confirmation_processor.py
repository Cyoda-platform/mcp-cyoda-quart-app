"""
OrderConfirmationProcessor for Purrfect Pets Application

Confirms order and validates payment as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.order.version_1.order import Order
from services.services import get_entity_service


class OrderConfirmationProcessor(CyodaProcessor):
    """
    Processor for confirming Order entities.
    Validates payment information and reserves the pet.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OrderConfirmationProcessor",
            description="Confirm order and validate payment"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Order entity for confirmation.

        Args:
            entity: The Order entity to confirm
            **kwargs: Additional processing parameters including payment data

        Returns:
            The confirmed Order entity
        """
        try:
            self.logger.info(
                f"Processing Order confirmation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Order for type-safe operations
            order = cast_entity(entity, Order)

            # Extract payment data from kwargs
            payment_data = kwargs.get('payment_data', {})
            
            # Validate payment information is complete
            if not order.payment_method:
                payment_method = payment_data.get('payment_method') or payment_data.get('paymentMethod')
                if payment_method:
                    order.payment_method = payment_method
                else:
                    raise ValueError("Payment method is required for order confirmation")

            # Process payment through payment gateway (simulated)
            payment_successful = self._process_payment(order, payment_data)
            
            if not payment_successful:
                raise ValueError("Payment processing failed")

            # Reserve the pet (trigger pet workflow to PENDING)
            entity_service = get_entity_service()
            try:
                # Trigger pet transition to pending state
                await entity_service.execute_transition(
                    entity_id=str(order.pet_id),
                    transition="transition_to_pending",
                    entity_class="Pet",
                    entity_version="1"
                )
                self.logger.info(f"Pet {order.pet_id} reserved for Order {order.technical_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to reserve pet {order.pet_id}: {str(e)}")
                raise ValueError(f"Pet reservation failed: {str(e)}")

            # Send order confirmation email (simulated)
            self._send_confirmation_email(order)

            # Set updated timestamp
            order.update_timestamp()

            self.logger.info(f"Order confirmation processed successfully for {order.technical_id}")
            return order

        except Exception as e:
            self.logger.error(
                f"Error processing Order confirmation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _process_payment(self, order: Order, payment_data: dict) -> bool:
        """
        Process payment through payment gateway (simulated).
        
        Args:
            order: The order to process payment for
            payment_data: Payment information
            
        Returns:
            True if payment successful, False otherwise
        """
        try:
            # Simulate payment processing
            self.logger.info(f"Processing payment for Order {order.technical_id}")
            
            # Basic validation
            if not order.total_amount or order.total_amount <= 0:
                self.logger.error("Invalid order total amount")
                return False
                
            if not order.payment_method:
                self.logger.error("No payment method specified")
                return False
            
            # Simulate successful payment
            self.logger.info(f"Payment of {order.total_amount} processed successfully via {order.payment_method}")
            return True
            
        except Exception as e:
            self.logger.error(f"Payment processing error: {str(e)}")
            return False

    def _send_confirmation_email(self, order: Order) -> None:
        """
        Send order confirmation email (simulated).
        
        Args:
            order: The confirmed order
        """
        try:
            self.logger.info(f"Sending confirmation email for Order {order.technical_id} to User {order.user_id}")
            # In a real implementation, this would send an actual email
            
        except Exception as e:
            self.logger.warning(f"Failed to send confirmation email: {str(e)}")
