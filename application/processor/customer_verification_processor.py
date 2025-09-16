"""
CustomerVerificationProcessor for Purrfect Pets API

Handles customer verification process including document validation.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.customer.version_1.customer import Customer
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CustomerVerificationProcessor(CyodaProcessor):
    """
    Processor for Customer verification.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerVerificationProcessor",
            description="Processes customer verification and document validation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process Customer verification according to functional requirements.

        Args:
            entity: The Customer entity to verify
            **kwargs: Additional processing parameters

        Returns:
            The processed customer entity
        """
        try:
            self.logger.info(
                f"Processing Customer verification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Get verification documents from kwargs
            verification_documents = kwargs.get("verification_documents", [])  # type: List[str]

            # 1. Validate identity documents
            await self._validate_identity_documents(customer, verification_documents)

            # 2. Verify contact information
            await self._verify_contact_information(customer)

            # 3. Check background if required (simulated)
            await self._check_background(customer)

            # 4. Validate address information
            await self._validate_address_information(customer)

            # 5. Update verification timestamp
            customer.add_metadata(
                "verification_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )
            customer.add_metadata("verification_documents", verification_documents)

            # 6. Send verification confirmation (simulated)
            await self._send_verification_confirmation(customer)

            # 7. Update customer state to VERIFIED (handled by workflow transition)
            self.logger.info(
                f"Customer verification {customer.technical_id} processed successfully"
            )

            return customer

        except Exception as e:
            self.logger.error(
                f"Error processing customer verification {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_identity_documents(
        self, customer: Customer, documents: list
    ) -> None:
        """
        Validate identity documents (simulated).

        Args:
            customer: The customer entity
            documents: List of document references
        """
        # In a real implementation, this would validate actual documents
        if not documents:
            self.logger.warning(
                f"No verification documents provided for customer {customer.technical_id}"
            )

        self.logger.info(
            f"Identity documents validated for customer {customer.technical_id}"
        )

    async def _verify_contact_information(self, customer: Customer) -> None:
        """
        Verify contact information (simulated).

        Args:
            customer: The customer entity
        """
        # In a real implementation, this would verify phone and email
        self.logger.info(
            f"Contact information verified for customer {customer.technical_id}"
        )

    async def _check_background(self, customer: Customer) -> None:
        """
        Check background if required (simulated).

        Args:
            customer: The customer entity
        """
        # In a real implementation, this might run background checks
        self.logger.info(
            f"Background check completed for customer {customer.technical_id}"
        )

    async def _validate_address_information(self, customer: Customer) -> None:
        """
        Validate address information (simulated).

        Args:
            customer: The customer entity
        """
        # In a real implementation, this would validate the address
        self.logger.info(
            f"Address information validated for customer {customer.technical_id}"
        )

    async def _send_verification_confirmation(self, customer: Customer) -> None:
        """
        Send verification confirmation (simulated).

        Args:
            customer: The customer entity
        """
        # In a real implementation, this would send an email/SMS
        self.logger.info(
            f"Verification confirmation sent to {customer.email} for customer {customer.get_full_name()}"
        )
