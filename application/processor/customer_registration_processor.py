"""
CustomerRegistrationProcessor for Purrfect Pets API

Handles customer registration process including validation and welcome email.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.customer.version_1.customer import Customer


class CustomerRegistrationProcessor(CyodaProcessor):
    """
    Processor for Customer registration.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerRegistrationProcessor",
            description="Processes customer registration and setup",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process Customer registration according to functional requirements.

        Args:
            entity: The Customer entity to register
            **kwargs: Additional processing parameters

        Returns:
            The processed customer entity
        """
        try:
            self.logger.info(
                f"Processing Customer registration {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # 1. Validate email uniqueness (simulated - would check database)
            await self._validate_email_uniqueness(customer.email)

            # 2. Validate required fields completeness (already done by Pydantic)
            
            # 3. Generate customer ID (handled by Cyoda)
            
            # 4. Set registration timestamp
            if not customer.registration_date:
                customer.registration_date = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # 5. Send welcome email with verification link (simulated)
            await self._send_welcome_email(customer)

            # 6. Create customer profile (add metadata)
            customer.add_metadata("profile_created", True)
            customer.add_metadata("registration_source", "web")

            # 7. Initialize adoption history
            customer.add_metadata("adoption_history", [])
            customer.add_metadata("application_count", 0)

            # 8. Update customer state to REGISTERED (handled by workflow transition)
            self.logger.info(
                f"Customer registration {customer.technical_id} processed successfully"
            )

            return customer

        except Exception as e:
            self.logger.error(
                f"Error processing customer registration {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_email_uniqueness(self, email: str) -> None:
        """
        Validate email uniqueness (simulated).

        Args:
            email: Email to validate

        Raises:
            ValueError: If email already exists
        """
        # In a real implementation, this would check the database
        # For now, we'll just log the validation
        self.logger.info(f"Email uniqueness validated for: {email}")

    async def _send_welcome_email(self, customer: Customer) -> None:
        """
        Send welcome email with verification link (simulated).

        Args:
            customer: The customer entity
        """
        # In a real implementation, this would send an actual email
        self.logger.info(
            f"Welcome email sent to {customer.email} for customer {customer.get_full_name()}"
        )
