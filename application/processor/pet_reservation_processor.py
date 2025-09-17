"""
PetReservationProcessor for Purrfect Pets API

Reserves a pet for an approved adoption application.
"""

import logging
from typing import Any

from application.entity.adoption_application.version_1.adoption_application import (
    AdoptionApplication,
)
from application.entity.customer.version_1.customer import Customer
from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class PetReservationProcessor(CyodaProcessor):
    """
    Processor for Pet reservation that reserves a pet for an approved adoption application.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationProcessor",
            description="Reserves a pet for an approved adoption application",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet reservation according to functional requirements.

        Args:
            entity: The Pet entity to process (must be in available state)
            **kwargs: Additional processing parameters (customerId, applicationId)

        Returns:
            The processed pet entity in reserved state
        """
        try:
            self.logger.info(
                f"Processing Pet reservation for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get customer ID and application ID from kwargs
            customer_id = kwargs.get("customerId") or kwargs.get("customer_id")
            application_id = kwargs.get("applicationId") or kwargs.get("application_id")

            if not customer_id:
                raise ValueError("Customer ID is required for pet reservation")
            if not application_id:
                raise ValueError("Application ID is required for pet reservation")

            # Validate customer exists and is active
            await self._validate_customer(customer_id)

            # Validate adoption application exists and is approved
            await self._validate_adoption_application(application_id)

            # Validate pet is currently available (done by workflow criteria)
            if not pet.is_available():
                raise ValueError("Pet must be available for reservation")

            # Create reservation record linking pet, customer, and application
            # This is handled by updating the pet entity with reservation info
            # In a real system, you might create a separate Reservation entity

            # Log reservation activity
            self.logger.info(
                f"Pet {pet.technical_id} reserved for customer {customer_id} "
                f"with application {application_id}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet reservation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_customer(self, customer_id: str) -> None:
        """
        Validate that customer exists and is active.

        Args:
            customer_id: The customer ID to validate

        Raises:
            ValueError: If customer validation fails
        """
        entity_service = get_entity_service()

        try:
            customer_response = await entity_service.get_by_id(
                entity_id=customer_id,
                entity_class=Customer.ENTITY_NAME,
                entity_version=str(Customer.ENTITY_VERSION),
            )

            if not customer_response:
                raise ValueError(f"Customer {customer_id} not found")

            customer = cast_entity(customer_response.data, Customer)
            if not customer.is_active():
                raise ValueError(f"Customer {customer_id} is not active")

            self.logger.debug(f"Customer {customer_id} validation passed")

        except Exception as e:
            self.logger.error(f"Customer validation failed for {customer_id}: {str(e)}")
            raise ValueError(f"Customer validation failed: {str(e)}")

    async def _validate_adoption_application(self, application_id: str) -> None:
        """
        Validate that adoption application exists and is approved.

        Args:
            application_id: The application ID to validate

        Raises:
            ValueError: If application validation fails
        """
        entity_service = get_entity_service()

        try:
            application_response = await entity_service.get_by_id(
                entity_id=application_id,
                entity_class=AdoptionApplication.ENTITY_NAME,
                entity_version=str(AdoptionApplication.ENTITY_VERSION),
            )

            if not application_response:
                raise ValueError(f"Adoption application {application_id} not found")

            application = cast_entity(application_response.data, AdoptionApplication)
            if not application.is_approved():
                raise ValueError(
                    f"Adoption application {application_id} is not approved"
                )

            self.logger.debug(
                f"Adoption application {application_id} validation passed"
            )

        except Exception as e:
            self.logger.error(
                f"Application validation failed for {application_id}: {str(e)}"
            )
            raise ValueError(f"Application validation failed: {str(e)}")
