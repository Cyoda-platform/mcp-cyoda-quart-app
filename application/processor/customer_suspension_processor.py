"""
CustomerSuspensionProcessor for Purrfect Pets API

Suspends a customer account due to policy violations.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.customer.version_1.customer import Customer


class CustomerSuspensionProcessor(CyodaProcessor):
    """
    Processor for Customer suspension that suspends a customer account due to policy violations.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerSuspensionProcessor",
            description="Suspends a customer account due to policy violations",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Customer suspension according to functional requirements.

        Args:
            entity: The Customer entity to process (must be active)
            **kwargs: Additional processing parameters (suspension reason, duration)

        Returns:
            The processed customer entity in suspended state
        """
        try:
            self.logger.info(
                f"Processing Customer suspension for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Get suspension information from kwargs
            suspension_reason = kwargs.get("suspensionReason") or kwargs.get("suspension_reason")
            suspension_duration = kwargs.get("suspensionDuration") or kwargs.get("suspension_duration")

            # Validate customer is currently active
            if not customer.is_active():
                raise ValueError("Customer must be active to suspend")

            # Validate suspension reason is provided
            if not suspension_reason:
                raise ValueError("Suspension reason is required")

            # Create suspension record with reason and duration
            # In a real system, you might create a separate CustomerSuspension entity
            suspension_info = f"Suspended: {suspension_reason}"
            if suspension_duration:
                suspension_info += f" (Duration: {suspension_duration})"

            # Cancel any pending adoption applications (in a real system)
            # This would involve finding all pending applications for this customer and cancelling them
            self.logger.info(
                f"Would cancel pending adoption applications for customer {customer.technical_id}"
            )

            # Notify customer of suspension (in a real system)
            # This would send an email or other notification to the customer
            self.logger.info(
                f"Would notify customer {customer.email} of account suspension"
            )

            # Log suspension activity
            self.logger.info(
                f"Customer {customer.technical_id} ({customer.get_full_name()}) suspended. {suspension_info}"
            )

            return customer

        except Exception as e:
            self.logger.error(
                f"Error processing customer suspension {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
