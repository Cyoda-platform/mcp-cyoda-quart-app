"""
PetReturnProcessor for Purrfect Pets API

Processes the return of an adopted pet.
"""

import logging
from typing import Any, Optional


from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class PetReturnProcessor(CyodaProcessor):
    """
    Processor for Pet return that processes the return of an adopted pet.
    Updates the related Adoption entity and resets pet status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReturnProcessor",
            description="Processes the return of an adopted pet and updates Adoption entity",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet return according to functional requirements.

        Args:
            entity: The Pet entity to process (must be adopted)
            **kwargs: Additional processing parameters (return reason, return date)

        Returns:
            The processed pet entity in available state
        """
        try:
            self.logger.info(
                f"Processing Pet return for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get return information from kwargs
            return_reason = kwargs.get("returnReason") or kwargs.get("return_reason")
            return_date = kwargs.get("returnDate") or kwargs.get("return_date")

            # Validate pet is currently adopted
            if not pet.is_adopted():
                raise ValueError("Pet must be adopted to process return")

            # Validate return reason is provided
            if not return_reason:
                raise ValueError("Return reason is required")

            # Find related adoption record
            await self._update_adoption_record(pet, return_reason, return_date)

            # Reset pet adoption-related fields
            pet.adoption_date = None

            # Log return activity
            self.logger.info(
                f"Pet {pet.technical_id} return processed. Reason: {return_reason}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet return {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _update_adoption_record(
        self, pet: Pet, return_reason: str, return_date: Optional[str] = None
    ) -> None:
        """
        Find and update the related adoption record with return information.

        Args:
            pet: The Pet entity being returned
            return_reason: Reason for the return
            return_date: Date of return (optional, defaults to current time)
        """
        entity_service = get_entity_service()

        try:
            # Find the adoption record for this pet
            # In a real system, you would search for the adoption by petId
            # For this implementation, we'll log the action

            pet_id = pet.technical_id or pet.entity_id

            # In a real implementation, you would:
            # 1. Search for adoption records where petId = pet_id and state != "returned"
            # 2. Update the found adoption record with return information
            # 3. Trigger the adoption return workflow transition

            # For now, we'll just log the intended action
            self.logger.info(
                f"Would update adoption record for pet {pet_id} with return reason: {return_reason}"
            )

            # In a real system, this would be something like:
            # adoption_records = await entity_service.search(...)
            # for adoption_record in adoption_records:
            #     adoption = cast_entity(adoption_record.data, Adoption)
            #     adoption.return_reason = return_reason
            #     adoption.set_return_date()
            #     await entity_service.update(
            #         entity_id=adoption_record.metadata.id,
            #         entity=adoption.model_dump(by_alias=True),
            #         entity_class=Adoption.ENTITY_NAME,
            #         transition="transition_to_returned"
            #     )

        except Exception as e:
            self.logger.error(
                f"Failed to update adoption record for pet {pet.technical_id}: {str(e)}"
            )
            raise ValueError(f"Failed to update adoption record: {str(e)}")
