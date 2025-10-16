"""
PaymentInitiationProcessor for Cyoda OMS Application

Handles payment initiation and setup for dummy payment processing
as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.payment.version_1.payment import Payment


class PaymentInitiationProcessor(CyodaProcessor):
    """
    Processor for Payment that handles payment initiation.
    Sets up the payment for dummy processing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PaymentInitiationProcessor",
            description="Processes Payment initiation for dummy payment flow",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Payment to mark it as initiated.

        Args:
            entity: The Payment entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed payment marked as initiated
        """
        try:
            self.logger.info(
                f"Initiating Payment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Payment for type-safe operations
            payment = cast_entity(entity, Payment)

            # Mark payment as initiated
            payment.mark_initiated()

            self.logger.info(
                f"Payment {payment.technical_id} initiated for amount ${payment.amount:.2f}"
            )

            return payment

        except Exception as e:
            self.logger.error(
                f"Error initiating payment for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
