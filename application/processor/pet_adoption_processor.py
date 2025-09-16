"""
PetAdoptionProcessor for Purrfect Pets API

Handles the final adoption process when a pet is adopted by a customer.
Validates adoption application, processes payment, and creates adoption records.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from application.entity.adoptionapplication.version_1.adoptionapplication import AdoptionApplication
from application.entity.petcarerecord.version_1.petcarerecord import PetCareRecord
from services.services import get_entity_service


class PetAdoptionProcessor(CyodaProcessor):
    """
    Processor for Pet adoption that handles the final adoption process.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAdoptionProcessor",
            description="Processes pet adoptions and finalizes adoption records",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet adoption according to functional requirements.

        Args:
            entity: The Pet entity to adopt
            **kwargs: Additional processing parameters (should include application_id)

        Returns:
            The processed pet entity with adoption information
        """
        try:
            self.logger.info(
                f"Processing Pet adoption {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get application ID from kwargs
            application_id = kwargs.get("application_id")
            if not application_id:
                raise ValueError("Adoption application ID is required for pet adoption")

            # 1. Validate adoption application approval
            adoption_application = await self._validate_adoption_application(application_id)

            # 2. Process adoption fee payment (simulated)
            await self._process_adoption_payment(pet, adoption_application)

            # 3. Generate adoption certificate (simulated)
            certificate_id = await self._generate_adoption_certificate(pet, adoption_application)

            # 4. Update pet ownership records
            pet.add_metadata("adoption_date", 
                           datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
            pet.add_metadata("adoption_certificate_id", certificate_id)
            pet.add_metadata("adoption_application_id", application_id)

            # 5. Send adoption confirmation to customer (simulated)
            await self._send_adoption_confirmation(adoption_application.customer_id, pet)

            # 6. Schedule post-adoption follow-up (simulated)
            await self._schedule_post_adoption_followup(adoption_application.customer_id, pet)

            # 7. Create final care record for adoption
            await self._create_adoption_care_record(pet)

            # 8. Update pet state to ADOPTED (handled by workflow transition)
            # Also update the adoption application to APPROVED
            await self._update_adoption_application(application_id)

            self.logger.info(
                f"Pet adoption {pet.technical_id} processed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet adoption {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_adoption_application(self, application_id: str) -> AdoptionApplication:
        """
        Validate that the adoption application is approved.

        Args:
            application_id: The adoption application ID

        Returns:
            The validated adoption application

        Raises:
            ValueError: If application is not found or not approved
        """
        entity_service = get_entity_service()

        try:
            # Get adoption application by ID
            app_response = await entity_service.get_by_id(
                entity_id=application_id,
                entity_class=AdoptionApplication.ENTITY_NAME,
                entity_version=str(AdoptionApplication.ENTITY_VERSION),
            )

            if not app_response:
                raise ValueError(f"Adoption application {application_id} not found")

            application = cast_entity(app_response.data, AdoptionApplication)

            # Check if application is approved
            if not application.is_approved():
                raise ValueError(f"Adoption application {application_id} is not approved")

            self.logger.info(f"Adoption application {application_id} validated successfully")
            return application

        except Exception as e:
            self.logger.error(f"Adoption application validation failed: {str(e)}")
            raise

    async def _process_adoption_payment(self, pet: Pet, application: AdoptionApplication) -> None:
        """
        Process adoption fee payment (simulated).

        Args:
            pet: The pet being adopted
            application: The adoption application
        """
        # In a real implementation, this would process payment
        total_fee = pet.price + application.application_fee
        self.logger.info(
            f"Adoption payment of ${total_fee} processed for pet {pet.technical_id}"
        )

    async def _generate_adoption_certificate(self, pet: Pet, application: AdoptionApplication) -> str:
        """
        Generate adoption certificate (simulated).

        Args:
            pet: The pet being adopted
            application: The adoption application

        Returns:
            Certificate ID
        """
        # In a real implementation, this would generate a PDF certificate
        certificate_id = f"CERT-{pet.technical_id}-{application.customer_id}"
        self.logger.info(
            f"Adoption certificate {certificate_id} generated for pet {pet.technical_id}"
        )
        return certificate_id

    async def _send_adoption_confirmation(self, customer_id: int, pet: Pet) -> None:
        """
        Send adoption confirmation to customer (simulated).

        Args:
            customer_id: The customer ID
            pet: The adopted pet
        """
        # In a real implementation, this would send an email with certificate
        self.logger.info(
            f"Adoption confirmation sent to customer {customer_id} for pet {pet.name}"
        )

    async def _schedule_post_adoption_followup(self, customer_id: int, pet: Pet) -> None:
        """
        Schedule post-adoption follow-up (simulated).

        Args:
            customer_id: The customer ID
            pet: The adopted pet
        """
        # In a real implementation, this would schedule follow-up tasks
        self.logger.info(
            f"Post-adoption follow-up scheduled for customer {customer_id} and pet {pet.technical_id}"
        )

    async def _create_adoption_care_record(self, pet: Pet) -> None:
        """
        Create final care record for adoption.

        Args:
            pet: The adopted pet
        """
        entity_service = get_entity_service()

        try:
            # Create adoption care record
            care_record = PetCareRecord(
                petId=int(pet.technical_id or pet.entity_id or "0"),
                careDate=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                careType="Other",
                description="Pet adoption completed - final health check and handover",
                veterinarian="Adoption Staff",
                cost=0.0,
                notes="Pet successfully adopted and handed over to new family",
            )

            # Convert to dict for EntityService.save()
            care_record_data = care_record.model_dump(by_alias=True)

            # Save the care record
            response = await entity_service.save(
                entity=care_record_data,
                entity_class=PetCareRecord.ENTITY_NAME,
                entity_version=str(PetCareRecord.ENTITY_VERSION),
            )

            created_record_id = response.metadata.id
            self.logger.info(
                f"Created adoption care record {created_record_id} for pet {pet.technical_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to create adoption care record for pet {pet.technical_id}: {str(e)}"
            )
            # Don't fail the entire adoption process if care record creation fails

    async def _update_adoption_application(self, application_id: str) -> None:
        """
        Update the adoption application to APPROVED state.

        Args:
            application_id: The adoption application ID
        """
        entity_service = get_entity_service()

        try:
            # Execute transition on the adoption application
            await entity_service.execute_transition(
                entity_id=application_id,
                transition="transition_to_approved",
                entity_class=AdoptionApplication.ENTITY_NAME,
                entity_version=str(AdoptionApplication.ENTITY_VERSION),
            )

            self.logger.info(f"Adoption application {application_id} updated to APPROVED")

        except Exception as e:
            self.logger.error(
                f"Failed to update adoption application {application_id}: {str(e)}"
            )
            # Don't fail the entire adoption process if application update fails
