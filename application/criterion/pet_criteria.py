"""
Pet Criteria for Purrfect Pets API

Validation criteria for pet-related business rules and workflows.
"""

import logging
from typing import Any

from application.entity.adoptionapplication.version_1.adoptionapplication import (
    AdoptionApplication,
)
from application.entity.customer.version_1.customer import Customer
from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class PetAvailabilityCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for checking if a pet is available for reservation.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAvailabilityCriterion",
            description="Validates that a pet is available for reservation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet is available for reservation.

        Args:
            entity: The Pet entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if the pet is available, False otherwise
        """
        try:
            self.logger.info(
                f"Validating pet availability {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Pet state must be AVAILABLE
            if not pet.is_available_for_adoption():
                self.logger.warning(
                    f"Pet {pet.technical_id} is not in AVAILABLE state: {pet.state}"
                )
                return False

            # Pet must not have any active reservations
            if pet.adopter_id is not None:
                self.logger.warning(
                    f"Pet {pet.technical_id} already has an active reservation: adopter {pet.adopter_id}"
                )
                return False

            # Pet must not be on medical hold
            if pet.is_on_medical_hold():
                self.logger.warning(f"Pet {pet.technical_id} is on medical hold")
                return False

            # Pet must have completed intake process (check for arrival date)
            if not pet.arrival_date:
                self.logger.warning(
                    f"Pet {pet.technical_id} has not completed intake process"
                )
                return False

            self.logger.info(f"Pet {pet.technical_id} passed availability validation")
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating pet availability {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False


class MedicalClearanceCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for checking if a pet is medically cleared for adoption.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MedicalClearanceCriterion",
            description="Validates that a pet is medically cleared for adoption",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet is medically cleared for adoption.

        Args:
            entity: The Pet entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if the pet is medically cleared, False otherwise
        """
        try:
            self.logger.info(
                f"Validating medical clearance {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # All required vaccinations must be up to date
            if not pet.vaccinated:
                self.logger.warning(
                    f"Pet {pet.technical_id} is not up to date with vaccinations"
                )
                return False

            # Recent health examination must be completed (check metadata)
            last_exam_date = pet.get_metadata("last_examination_date")
            if not last_exam_date:
                self.logger.warning(
                    f"Pet {pet.technical_id} has no recent health examination on record"
                )
                return False

            # No active medical conditions requiring treatment
            if pet.is_on_medical_hold():
                self.logger.warning(
                    f"Pet {pet.technical_id} is currently on medical hold"
                )
                return False

            # Check for any ongoing medical issues in metadata
            medical_issues = pet.get_metadata("medical_issues", [])
            if medical_issues:
                self.logger.warning(
                    f"Pet {pet.technical_id} has ongoing medical issues: {medical_issues}"
                )
                return False

            # Veterinarian clearance must be documented
            vet_clearance = pet.get_metadata("veterinarian_clearance")
            if not vet_clearance:
                self.logger.warning(
                    f"Pet {pet.technical_id} lacks veterinarian clearance documentation"
                )
                return False

            self.logger.info(
                f"Pet {pet.technical_id} passed medical clearance validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating medical clearance {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False


class AdoptionApprovalCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for checking if an adoption can proceed.
    This criterion validates both the pet and adoption application.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AdoptionApprovalCriterion",
            description="Validates that an adoption can proceed",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the adoption can proceed.

        Args:
            entity: The Pet entity to validate
            **kwargs: Additional criteria parameters (should include application_id)

        Returns:
            True if the adoption can proceed, False otherwise
        """
        try:
            self.logger.info(
                f"Validating adoption approval {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get application ID from kwargs
            application_id = kwargs.get("application_id")
            if not application_id:
                self.logger.warning(
                    "No application ID provided for adoption approval validation"
                )
                return False

            # Pet must be in RESERVED state
            if not pet.is_reserved():
                self.logger.warning(
                    f"Pet {pet.technical_id} is not in RESERVED state: {pet.state}"
                )
                return False

            # Validate adoption application
            if not await self._validate_adoption_application(application_id):
                return False

            # Validate customer
            if not await self._validate_customer(pet.adopter_id):
                return False

            # All adoption fees must be paid (simulated check)
            if not await self._validate_fees_paid(application_id):
                return False

            # Adoption paperwork must be completed (simulated check)
            if not await self._validate_paperwork_completed(application_id):
                return False

            self.logger.info(
                f"Pet {pet.technical_id} passed adoption approval validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating adoption approval {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _validate_adoption_application(self, application_id: str) -> bool:
        """
        Validate that the adoption application is approved.

        Args:
            application_id: The adoption application ID

        Returns:
            True if application is approved, False otherwise
        """
        try:
            entity_service = get_entity_service()

            app_response = await entity_service.get_by_id(
                entity_id=application_id,
                entity_class=AdoptionApplication.ENTITY_NAME,
                entity_version=str(AdoptionApplication.ENTITY_VERSION),
            )

            if not app_response:
                self.logger.warning(f"Adoption application {application_id} not found")
                return False

            application = cast_entity(app_response.data, AdoptionApplication)

            if not application.is_approved():
                self.logger.warning(
                    f"Adoption application {application_id} is not approved: {application.state}"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(
                f"Error validating adoption application {application_id}: {str(e)}"
            )
            return False

    async def _validate_customer(self, customer_id: int) -> bool:
        """
        Validate that the customer is approved.

        Args:
            customer_id: The customer ID

        Returns:
            True if customer is approved, False otherwise
        """
        if not customer_id:
            self.logger.warning("No customer ID provided")
            return False

        try:
            entity_service = get_entity_service()

            customer_response = await entity_service.get_by_id(
                entity_id=str(customer_id),
                entity_class=Customer.ENTITY_NAME,
                entity_version=str(Customer.ENTITY_VERSION),
            )

            if not customer_response:
                self.logger.warning(f"Customer {customer_id} not found")
                return False

            customer = cast_entity(customer_response.data, Customer)

            if not customer.is_approved():
                self.logger.warning(
                    f"Customer {customer_id} is not approved: {customer.state}"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating customer {customer_id}: {str(e)}")
            return False

    async def _validate_fees_paid(self, application_id: str) -> bool:
        """
        Validate that all adoption fees are paid (simulated).

        Args:
            application_id: The adoption application ID

        Returns:
            True if fees are paid, False otherwise
        """
        # In a real implementation, this would check payment records
        self.logger.info(f"Adoption fees validated for application {application_id}")
        return True

    async def _validate_paperwork_completed(self, application_id: str) -> bool:
        """
        Validate that adoption paperwork is completed (simulated).

        Args:
            application_id: The adoption application ID

        Returns:
            True if paperwork is completed, False otherwise
        """
        # In a real implementation, this would check document completion
        self.logger.info(
            f"Adoption paperwork validated for application {application_id}"
        )
        return True
