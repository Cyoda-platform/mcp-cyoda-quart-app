"""
PetReservationProcessor for Purrfect Pets API

Handles the reservation process when a customer reserves a pet for adoption.
Validates customer eligibility, sets adopter ID, and records reservation timestamp.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from application.entity.customer.version_1.customer import Customer
from services.services import get_entity_service


class PetReservationProcessor(CyodaProcessor):
    """
    Processor for Pet reservation that handles customer reservations.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationProcessor",
            description="Processes pet reservations for customers",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet reservation according to functional requirements.

        Args:
            entity: The Pet entity to reserve
            **kwargs: Additional processing parameters (should include customer_id)

        Returns:
            The processed pet entity with reservation information
        """
        try:
            self.logger.info(
                f"Processing Pet reservation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get customer ID from kwargs (this would be passed from the route)
            customer_id = kwargs.get("customer_id")
            if not customer_id:
                raise ValueError("Customer ID is required for pet reservation")

            # 1. Validate customer eligibility for reservation
            await self._validate_customer_eligibility(customer_id)

            # 2. Check if pet is currently available
            if not pet.is_available_for_adoption():
                raise ValueError(
                    f"Pet {pet.technical_id} is not available for reservation"
                )

            # 3. Set adopter ID to the customer
            pet.adopter_id = int(customer_id)

            # 4. Record reservation timestamp
            pet.add_metadata(
                "reservation_timestamp",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )

            # 5. Send reservation confirmation to customer (simulated)
            await self._send_reservation_confirmation(customer_id, pet)

            # 6. Schedule follow-up reminder for reservation expiry (simulated)
            await self._schedule_reservation_reminder(customer_id, pet)

            # 7. Update pet state to RESERVED (handled by workflow transition)
            self.logger.info(
                f"Pet reservation {pet.technical_id} processed successfully for customer {customer_id}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet reservation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_customer_eligibility(self, customer_id: str) -> None:
        """
        Validate that the customer is eligible for pet reservation.

        Args:
            customer_id: The customer ID to validate

        Raises:
            ValueError: If customer is not eligible
        """
        entity_service = get_entity_service()

        try:
            # Get customer by ID
            customer_response = await entity_service.get_by_id(
                entity_id=customer_id,
                entity_class=Customer.ENTITY_NAME,
                entity_version=str(Customer.ENTITY_VERSION),
            )

            if not customer_response:
                raise ValueError(f"Customer {customer_id} not found")

            customer = cast_entity(customer_response.data, Customer)

            # Check if customer is approved for adoptions
            if not customer.is_approved():
                raise ValueError(
                    f"Customer {customer_id} is not approved for adoptions"
                )

            self.logger.info(
                f"Customer {customer_id} eligibility validated successfully"
            )

        except Exception as e:
            self.logger.error(f"Customer eligibility validation failed: {str(e)}")
            raise

    async def _send_reservation_confirmation(self, customer_id: str, pet: Pet) -> None:
        """
        Send reservation confirmation to customer (simulated).

        Args:
            customer_id: The customer ID
            pet: The reserved pet
        """
        # In a real implementation, this would send an email or SMS
        self.logger.info(
            f"Reservation confirmation sent to customer {customer_id} for pet {pet.name} ({pet.technical_id})"
        )

    async def _schedule_reservation_reminder(self, customer_id: str, pet: Pet) -> None:
        """
        Schedule follow-up reminder for reservation expiry (simulated).

        Args:
            customer_id: The customer ID
            pet: The reserved pet
        """
        # In a real implementation, this would schedule a reminder task
        self.logger.info(
            f"Reservation reminder scheduled for customer {customer_id} and pet {pet.technical_id}"
        )
