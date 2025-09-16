"""
PetIntakeProcessor for Purrfect Pets API

Handles the intake process for new pets arriving at the store.
Validates pet data, sets arrival date, initializes health records, and creates initial care record.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from application.entity.petcarerecord.version_1.petcarerecord import PetCareRecord
from services.services import get_entity_service


class PetIntakeProcessor(CyodaProcessor):
    """
    Processor for Pet intake that handles the initial processing when a pet arrives.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetIntakeProcessor",
            description="Processes new pet intake, validates data and creates initial care record",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet intake according to functional requirements.

        Args:
            entity: The Pet entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet intake {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # 1. Validate pet data completeness (already done by Pydantic)
            # 2. Assign unique pet ID (handled by Cyoda)
            # 3. Set arrival date to current timestamp
            if not pet.arrival_date:
                pet.arrival_date = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            # 4. Initialize health and vaccination records (set defaults if not provided)
            if pet.vaccinated is None:
                pet.vaccinated = False
            if pet.neutered is None:
                pet.neutered = False
            if pet.microchipped is None:
                pet.microchipped = False

            # 5. Generate default description if not provided
            if not pet.description or len(pet.description.strip()) == 0:
                pet.description = f"Beautiful {pet.age}-year-old {pet.breed} {pet.category.lower()} looking for a loving home."

            # 6. Set initial price based on category and breed (if not already set)
            if pet.price <= 0:
                pet.price = self._calculate_initial_price(
                    pet.category, pet.breed, pet.age
                )

            # 7. Create initial pet care record for intake examination
            await self._create_intake_care_record(pet)

            # 8. Update pet state to AVAILABLE (handled by workflow transition)
            self.logger.info(f"Pet intake {pet.technical_id} processed successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet intake {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_initial_price(self, category: str, breed: str, age: int) -> float:
        """
        Calculate initial price based on category, breed, and age.

        Args:
            category: Pet category
            breed: Pet breed
            age: Pet age

        Returns:
            Calculated price
        """
        base_prices = {
            "Dog": 300.0,
            "Cat": 150.0,
            "Bird": 100.0,
            "Fish": 25.0,
            "Rabbit": 75.0,
            "Hamster": 30.0,
            "Guinea Pig": 50.0,
            "Reptile": 100.0,
        }

        base_price = base_prices.get(category, 100.0)

        # Adjust for age (younger pets typically cost more)
        if age < 1:
            base_price *= 1.5
        elif age < 3:
            base_price *= 1.2
        elif age > 8:
            base_price *= 0.8

        # Premium breeds cost more
        premium_breeds = [
            "Golden Retriever",
            "Labrador",
            "Persian",
            "Siamese",
            "Maine Coon",
        ]
        if breed in premium_breeds:
            base_price *= 1.3

        return round(base_price, 2)

    async def _create_intake_care_record(self, pet: Pet) -> None:
        """
        Create initial care record for intake examination.

        Args:
            pet: The pet entity
        """
        entity_service = get_entity_service()

        try:
            # Create intake examination record
            care_record = PetCareRecord(
                petId=int(pet.technical_id or pet.entity_id or "0"),
                careDate=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                careType="Checkup",
                description="Initial intake examination and health assessment",
                veterinarian="Intake Staff",
                cost=0.0,
                notes="Pet intake examination completed successfully",
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
                f"Created intake care record {created_record_id} for pet {pet.technical_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to create intake care record for pet {pet.technical_id}: {str(e)}"
            )
            # Don't fail the entire intake process if care record creation fails
            pass
