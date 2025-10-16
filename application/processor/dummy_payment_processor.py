"""
DummyPaymentProcessor for Cyoda OMS Application

Handles dummy payment processing with auto-approval after ~3 seconds
as specified in functional requirements.
"""

import asyncio
import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.payment.version_1.payment import Payment


class DummyPaymentProcessor(CyodaProcessor):
    """
    Processor for Payment that handles dummy payment processing.
    Auto-approves payments after approximately 3 seconds.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DummyPaymentProcessor",
            description="Processes dummy payments with auto-approval after 3 seconds",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Payment with dummy auto-approval.

        Args:
            entity: The Payment entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed payment marked as paid
        """
        try:
            self.logger.info(
                f"Processing dummy payment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Payment for type-safe operations
            payment = cast_entity(entity, Payment)

            # Simulate payment processing delay (~3 seconds)
            self.logger.info(f"Payment {payment.technical_id} processing for 3 seconds...")
            await asyncio.sleep(3)

            # Auto-approve the payment (dummy implementation)
            payment.mark_paid()

            self.logger.info(
                f"Payment {payment.technical_id} auto-approved for amount ${payment.amount:.2f}"
            )

            return payment

        except Exception as e:
            self.logger.error(
                f"Error processing dummy payment for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
