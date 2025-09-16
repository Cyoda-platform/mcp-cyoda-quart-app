"""
PetMedicalHoldProcessor for Purrfect Pets API

Handles placing pets on medical hold when they require medical attention.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from application.entity.petcarerecord.version_1.petcarerecord import PetCareRecord
from services.services import get_entity_service


class PetMedicalHoldProcessor(CyodaProcessor):
    """
    Processor for placing pets on medical hold.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetMedicalHoldProcessor",
            description="Processes pets being placed on medical hold",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process placing the Pet on medical hold.

        Args:
            entity: The Pet entity to place on medical hold
            **kwargs: Additional processing parameters (should include medical_reason)

        Returns:
            The processed pet entity with medical hold information
        """
        try:
            self.logger.info(
                f"Processing Pet medical hold {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get medical reason from kwargs
            medical_reason = kwargs.get("medical_reason", "Medical attention required")

            # 1. Record medical hold reason
            pet.add_metadata("medical_hold_reason", medical_reason)
            pet.add_metadata(
                "medical_hold_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )

            # 2. Schedule veterinary examination (simulated)
            await self._schedule_veterinary_examination(pet, medical_reason)

            # 3. Notify adoption staff of medical hold (simulated)
            await self._notify_adoption_staff(pet, medical_reason)

            # 4. Cancel any existing reservations
            if pet.adopter_id:
                await self._cancel_existing_reservation(pet)

            # 5. Create medical care record
            await self._create_medical_care_record(pet, medical_reason)

            # 6. Update pet state to MEDICAL_HOLD (handled by workflow transition)
            self.logger.info(
                f"Pet medical hold {pet.technical_id} processed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet medical hold {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _schedule_veterinary_examination(
        self, pet: Pet, medical_reason: str
    ) -> None:
        """
        Schedule veterinary examination (simulated).

        Args:
            pet: The pet entity
            medical_reason: Reason for medical hold
        """
        # In a real implementation, this would schedule an appointment
        self.logger.info(
            f"Veterinary examination scheduled for pet {pet.technical_id} - Reason: {medical_reason}"
        )

    async def _notify_adoption_staff(self, pet: Pet, medical_reason: str) -> None:
        """
        Notify adoption staff of medical hold (simulated).

        Args:
            pet: The pet entity
            medical_reason: Reason for medical hold
        """
        # In a real implementation, this would send notifications to staff
        self.logger.info(
            f"Adoption staff notified of medical hold for pet {pet.name} ({pet.technical_id}) - Reason: {medical_reason}"
        )

    async def _cancel_existing_reservation(self, pet: Pet) -> None:
        """
        Cancel any existing reservations.

        Args:
            pet: The pet entity
        """
        customer_id = pet.adopter_id
        pet.adopter_id = None

        if pet.metadata and "reservation_timestamp" in pet.metadata:
            del pet.metadata["reservation_timestamp"]

        # Notify customer of cancellation due to medical hold
        if customer_id:
            self.logger.info(
                f"Reservation cancelled for customer {customer_id} due to medical hold on pet {pet.technical_id}"
            )

    async def _create_medical_care_record(self, pet: Pet, medical_reason: str) -> None:
        """
        Create medical care record.

        Args:
            pet: The pet entity
            medical_reason: Reason for medical hold
        """
        entity_service = get_entity_service()

        try:
            # Create medical care record
            care_record = PetCareRecord(
                petId=int(pet.technical_id or pet.entity_id or "0"),
                careDate=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                careType="Treatment",
                description=f"Medical hold initiated - {medical_reason}",
                veterinarian="Medical Staff",
                cost=0.0,
                notes=f"Pet placed on medical hold for: {medical_reason}",
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
                f"Created medical care record {created_record_id} for pet {pet.technical_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to create medical care record for pet {pet.technical_id}: {str(e)}"
            )
            # Don't fail the entire process if care record creation fails
