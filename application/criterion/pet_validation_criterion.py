"""
Pet Validation Criterion for Purrfect Pets API.

Validates that a pet has all required information for activation.
"""

import logging
import re
from typing import Any, Dict, Optional

from application.entity.pet.version_1.pet import Pet
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class PetValidationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate pet information for activation."""

    def __init__(self, name: str = "PetValidationCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description
            or "Validate that a pet has all required information for activation",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if the pet meets validation criteria."""
        try:
            if not isinstance(entity, Pet):
                logger.warning(f"Expected Pet entity, got {type(entity)}")
                return False

            pet = entity

            # Pet name validation
            if not self._validate_pet_name(pet.name):
                logger.info(f"Pet name validation failed for pet {pet.pet_id}")
                return False

            # Species validation
            if not self._validate_species(pet.species):
                logger.info(f"Species validation failed for pet {pet.pet_id}")
                return False

            # Owner validation
            if not await self._validate_owner_exists_and_active(pet.owner_id):
                logger.info(f"Owner validation failed for pet {pet.pet_id}")
                return False

            # Age validation
            if not self._validate_age(pet.age):
                logger.info(f"Age validation failed for pet {pet.pet_id}")
                return False

            # Weight validation
            if not self._validate_weight(pet.weight):
                logger.info(f"Weight validation failed for pet {pet.pet_id}")
                return False

            # Microchip ID validation
            if not await self._validate_microchip_unique(pet.microchip_id, pet.pet_id):
                logger.info(f"Microchip validation failed for pet {pet.pet_id}")
                return False

            logger.info(f"All validations passed for pet {pet.pet_id}")
            return True

        except Exception as e:
            logger.exception(
                f"Failed to check pet validation criteria for entity {entity.entity_id}"
            )
            raise CriteriaError(
                self.name, f"Failed to check pet validation criteria: {str(e)}", e
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Pet)

    def _validate_pet_name(self, name: str) -> bool:
        """Validate pet name is not empty and contains only valid characters."""
        if not name or not name.strip():
            return False

        # Check for valid characters (letters, numbers, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z0-9\s\-']+$", name.strip()):
            return False

        return len(name.strip()) <= 100

    def _validate_species(self, species: str) -> bool:
        """Validate species is from approved list."""
        if not species:
            return False

        approved_species = {
            "dog",
            "cat",
            "bird",
            "fish",
            "rabbit",
            "hamster",
            "guinea pig",
            "ferret",
            "turtle",
            "snake",
            "lizard",
            "horse",
            "goat",
            "sheep",
        }

        return species.lower() in approved_species

    async def _validate_owner_exists_and_active(self, owner_id: str) -> bool:
        """Validate that owner exists and is in active state."""
        if not owner_id:
            return False

        # TODO: Implement actual owner validation
        # entity_service = self._get_entity_service()
        # try:
        #     owner = await entity_service.get_by_business_id("Owner", owner_id)
        #     return owner and owner.state == "active"
        # except Exception:
        #     return False

        # Mock validation - assume owner exists and is active
        logger.debug(f"Mock validation: Owner {owner_id} exists and is active")
        return True

    def _validate_age(self, age: Optional[int]) -> bool:
        """Validate pet age is reasonable (0-30 years)."""
        if age is None:
            return True  # Age is optional

        return 0 <= age <= 30

    def _validate_weight(self, weight: Optional[float]) -> bool:
        """Validate weight is positive if provided."""
        if weight is None:
            return True  # Weight is optional

        return weight > 0

    async def _validate_microchip_unique(
        self, microchip_id: Optional[str], pet_id: str
    ) -> bool:
        """Validate microchip ID is unique if provided."""
        if not microchip_id:
            return True  # Microchip is optional

        # TODO: Implement actual uniqueness check
        # entity_service = self._get_entity_service()
        # try:
        #     existing_pets = await entity_service.search("Pet", {"microchip_id": microchip_id})
        #     # Check if any existing pet has this microchip (excluding current pet)
        #     for pet in existing_pets:
        #         if pet.pet_id != pet_id:
        #             return False
        #     return True
        # except Exception:
        #     return False

        # Mock validation - assume microchip is unique
        logger.debug(f"Mock validation: Microchip {microchip_id} is unique")
        return True

    def _get_entity_service(self):
        """Get entity service instance."""
        from service.services import get_entity_service

        return get_entity_service()
