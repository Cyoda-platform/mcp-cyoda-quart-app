"""
CustomerBlacklistProcessor for Purrfect Pets API

Blacklists a customer permanently.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.customer.version_1.customer import Customer


class CustomerBlacklistProcessor(CyodaProcessor):
    """
    Processor for Customer blacklisting that blacklists a customer permanently.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerBlacklistProcessor",
            description="Blacklists a customer permanently",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Customer blacklisting according to functional requirements.

        Args:
            entity: The Customer entity to process (must be active or suspended)
            **kwargs: Additional processing parameters (blacklist reason)

        Returns:
            The processed customer entity in blacklisted state
        """
        try:
            self.logger.info(
                f"Processing Customer blacklisting for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Get blacklist information from kwargs
            blacklist_reason = kwargs.get("blacklistReason") or kwargs.get("blacklist_reason")

            # Validate customer is currently active or suspended
            if customer.is_blacklisted():
                raise ValueError("Customer is already blacklisted")

            # Validate blacklist reason is provided
            if not blacklist_reason:
                raise ValueError("Blacklist reason is required")

            # Create blacklist record with reason
            # In a real system, you might create a separate CustomerBlacklist entity
            blacklist_info = f"Blacklisted: {blacklist_reason}"

            # Cancel all pending adoption applications (in a real system)
            # This would involve finding all pending applications for this customer and cancelling them
            self.logger.info(
                f"Would cancel all pending adoption applications for customer {customer.technical_id}"
            )

            # Revoke any current adoptions if necessary (in a real system)
            # This would be a serious action that might involve legal processes
            # For now, we just log the intent
            self.logger.info(
                f"Would review current adoptions for customer {customer.technical_id} for potential revocation"
            )

            # Notify relevant staff (in a real system)
            # This would send notifications to management and relevant staff
            self.logger.info(
                f"Would notify relevant staff of customer {customer.technical_id} blacklisting"
            )

            # Log blacklist activity
            self.logger.info(
                f"Customer {customer.technical_id} ({customer.get_full_name()}) blacklisted. {blacklist_info}"
            )

            return customer

        except Exception as e:
            self.logger.error(
                f"Error processing customer blacklisting {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
