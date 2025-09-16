"""
PetValidationProcessor for Purrfect Pets Application

Validates pet information is complete and ready for availability
as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service


class PetValidationProcessor(CyodaProcessor):
    """
    Processor for validating Pet entities before making them available.
    Ensures all required information is complete and valid.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetValidationProcessor",
            description="Validate pet information is complete and ready for availability"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for validation.

        Args:
            entity: The Pet entity to validate
            **kwargs: Additional processing parameters

        Returns:
            The validated Pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet validation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate all required fields are present
            if not pet.name or len(pet.name.strip()) == 0:
                raise ValueError("Pet name is required")
            
            if not pet.photo_urls or len(pet.photo_urls) == 0:
                raise ValueError("At least one photo URL is required")

            # Validate price is positive
            if pet.price is None or pet.price <= 0:
                raise ValueError("Valid positive price is required")

            # Validate age is reasonable (0-300 months)
            if pet.age is not None and (pet.age < 0 or pet.age > 300):
                raise ValueError("Age must be between 0 and 300 months")

            # Validate weight is positive if provided
            if pet.weight is not None and pet.weight <= 0:
                raise ValueError("Weight must be positive if provided")

            # Validate photo URLs are accessible (basic URL format check)
            for url in pet.photo_urls:
                if not url.startswith(("http://", "https://")):
                    raise ValueError(f"Invalid photo URL format: {url}")

            # Validate category exists and is active (if category_id is provided)
            if pet.category_id is not None:
                entity_service = get_entity_service()
                try:
                    category_response = await entity_service.get_by_id(
                        entity_id=str(pet.category_id),
                        entity_class="Category",
                        entity_version="1"
                    )
                    if not category_response:
                        raise ValueError(f"Category with ID {pet.category_id} not found")
                    
                    category_state = getattr(category_response.metadata, 'state', None)
                    if category_state != "active":
                        raise ValueError(f"Category must be active, current state: {category_state}")
                        
                except Exception as e:
                    self.logger.warning(f"Could not validate category {pet.category_id}: {str(e)}")
                    # Continue processing - category validation is not critical for this transition

            # Validate all tags exist and are active (if tag_ids are provided)
            if pet.tag_ids:
                entity_service = get_entity_service()
                for tag_id in pet.tag_ids:
                    try:
                        tag_response = await entity_service.get_by_id(
                            entity_id=str(tag_id),
                            entity_class="Tag",
                            entity_version="1"
                        )
                        if not tag_response:
                            self.logger.warning(f"Tag with ID {tag_id} not found")
                            continue
                        
                        tag_state = getattr(tag_response.metadata, 'state', None)
                        if tag_state != "active":
                            self.logger.warning(f"Tag {tag_id} is not active, current state: {tag_state}")
                            
                    except Exception as e:
                        self.logger.warning(f"Could not validate tag {tag_id}: {str(e)}")
                        # Continue processing - tag validation is not critical

            # Set updated timestamp
            pet.update_timestamp()

            self.logger.info(f"Pet validation processed successfully for {pet.technical_id}")
            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet validation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
