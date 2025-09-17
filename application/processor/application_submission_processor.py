"""
ApplicationSubmissionProcessor for Purrfect Pets API

Processes a new adoption application submission.
"""

import logging
from typing import Any

from application.entity.adoption_application.version_1.adoption_application import (
    AdoptionApplication,
)
from application.entity.customer.version_1.customer import Customer
from application.entity.pet.version_1.pet import Pet
from application.entity.store.version_1.store import Store
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ApplicationSubmissionProcessor(CyodaProcessor):
    """
    Processor for AdoptionApplication submission that processes a new adoption application.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationSubmissionProcessor",
            description="Processes a new adoption application submission",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the AdoptionApplication submission according to functional requirements.

        Args:
            entity: The AdoptionApplication entity to process (must be in initial state)
            **kwargs: Additional processing parameters

        Returns:
            The processed application entity in submitted state
        """
        try:
            self.logger.info(
                f"Processing AdoptionApplication submission for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AdoptionApplication for type-safe operations
            application = cast_entity(entity, AdoptionApplication)

            # Validate customer exists and is active
            await self._validate_customer(application.customer_id)

            # Validate pet exists and is available
            await self._validate_pet(application.pet_id)

            # Validate store exists and is active
            await self._validate_store(application.store_id)

            # Validate required application fields are complete
            self._validate_application_fields(application)

            # Set application date to current timestamp
            application.set_application_date()

            # Notify store staff of new application (in a real system)
            self.logger.info(
                f"Would notify store {application.store_id} staff of new application {application.technical_id}"
            )

            # Log application submission
            self.logger.info(
                f"AdoptionApplication {application.technical_id} submitted successfully"
            )

            return application

        except Exception as e:
            self.logger.error(
                f"Error processing application submission {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_customer(self, customer_id: int) -> None:
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
                entity_id=str(customer_id),
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

    async def _validate_pet(self, pet_id: int) -> None:
        """
        Validate that pet exists and is available.

        Args:
            pet_id: The pet ID to validate

        Raises:
            ValueError: If pet validation fails
        """
        entity_service = get_entity_service()

        try:
            pet_response = await entity_service.get_by_id(
                entity_id=str(pet_id),
                entity_class=Pet.ENTITY_NAME,
                entity_version=str(Pet.ENTITY_VERSION),
            )

            if not pet_response:
                raise ValueError(f"Pet {pet_id} not found")

            pet = cast_entity(pet_response.data, Pet)
            if not pet.is_available():
                raise ValueError(f"Pet {pet_id} is not available")

            self.logger.debug(f"Pet {pet_id} validation passed")

        except Exception as e:
            self.logger.error(f"Pet validation failed for {pet_id}: {str(e)}")
            raise ValueError(f"Pet validation failed: {str(e)}")

    async def _validate_store(self, store_id: int) -> None:
        """
        Validate that store exists and is active.

        Args:
            store_id: The store ID to validate

        Raises:
            ValueError: If store validation fails
        """
        entity_service = get_entity_service()

        try:
            store_response = await entity_service.get_by_id(
                entity_id=str(store_id),
                entity_class=Store.ENTITY_NAME,
                entity_version=str(Store.ENTITY_VERSION),
            )

            if not store_response:
                raise ValueError(f"Store {store_id} not found")

            store = cast_entity(store_response.data, Store)
            if not store.is_active():
                raise ValueError(f"Store {store_id} is not active")

            self.logger.debug(f"Store {store_id} validation passed")

        except Exception as e:
            self.logger.error(f"Store validation failed for {store_id}: {str(e)}")
            raise ValueError(f"Store validation failed: {str(e)}")

    def _validate_application_fields(self, application: AdoptionApplication) -> None:
        """
        Validate that required application fields are complete.

        Args:
            application: The AdoptionApplication entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Required fields are already validated by Pydantic model
        # Additional business logic validation can be added here

        if (
            not application.reason_for_adoption
            or len(application.reason_for_adoption.strip()) == 0
        ):
            raise ValueError("Reason for adoption is required")

        if (
            not application.living_arrangement
            or len(application.living_arrangement.strip()) == 0
        ):
            raise ValueError("Living arrangement description is required")

        if (
            not application.pet_care_experience
            or len(application.pet_care_experience.strip()) == 0
        ):
            raise ValueError("Pet care experience is required")

        self.logger.debug(f"Application fields validation passed")
