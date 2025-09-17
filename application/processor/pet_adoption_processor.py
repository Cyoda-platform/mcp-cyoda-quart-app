"""
PetAdoptionProcessor for Purrfect Pets API

Completes the adoption process for a reserved pet.
"""

import logging
from typing import Any, Dict

from application.entity.adoption.version_1.adoption import Adoption
from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class PetAdoptionProcessor(CyodaProcessor):
    """
    Processor for Pet adoption that completes the adoption process for a reserved pet.
    Creates an Adoption entity and updates the pet status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAdoptionProcessor",
            description="Completes the adoption process for a reserved pet and creates Adoption entity",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet adoption according to functional requirements.

        Args:
            entity: The Pet entity to process (must be in reserved state)
            **kwargs: Additional processing parameters (adoption details)

        Returns:
            The processed pet entity in adopted state
        """
        try:
            self.logger.info(
                f"Processing Pet adoption for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get adoption details from kwargs
            adoption_details = kwargs.get("adoptionDetails", {})

            # Validate pet is currently reserved (done by workflow criteria)
            if not pet.is_reserved():
                raise ValueError("Pet must be reserved before adoption")

            # Validate all adoption requirements are met
            self._validate_adoption_requirements(adoption_details)

            # Set adoption date to current timestamp
            pet.set_adoption_date()

            # Create adoption record with all details
            await self._create_adoption_record(pet, adoption_details)

            # Log adoption completion
            self.logger.info(f"Pet {pet.technical_id} adoption completed successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing pet adoption {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_adoption_requirements(self, adoption_details: Dict[str, Any]) -> None:
        """
        Validate that all adoption requirements are met.

        Args:
            adoption_details: Dictionary containing adoption details

        Raises:
            ValueError: If validation fails
        """
        # Contract must be signed
        if not adoption_details.get("contractSigned", False):
            raise ValueError("Adoption contract must be signed")

        # Fee must be received
        if not adoption_details.get("feeReceived", False):
            raise ValueError("Adoption fee must be received")

        # Adoption fee must be provided
        adoption_fee = adoption_details.get("adoptionFee")
        if adoption_fee is None or adoption_fee < 0:
            raise ValueError("Valid adoption fee must be provided")

        self.logger.debug("Adoption requirements validation passed")

    async def _create_adoption_record(self, pet: Pet, adoption_details: Dict[str, Any]) -> None:
        """
        Create adoption record with all details.

        Args:
            pet: The Pet entity being adopted
            adoption_details: Dictionary containing adoption details
        """
        entity_service = get_entity_service()

        try:
            # Extract required fields from adoption details
            customer_id = adoption_details.get("customerId")
            store_id = adoption_details.get("storeId")
            application_id = adoption_details.get("applicationId")
            adoption_fee = adoption_details.get("adoptionFee", 0.0)
            contract_signed = adoption_details.get("contractSigned", False)
            microchip_transferred = adoption_details.get("microchipTransferred", False)
            vaccination_records_provided = adoption_details.get(
                "vaccinationRecordsProvided", False
            )
            adoption_notes = adoption_details.get("adoptionNotes")

            if not customer_id:
                raise ValueError("Customer ID is required for adoption record")
            if not store_id:
                raise ValueError("Store ID is required for adoption record")
            if not application_id:
                raise ValueError("Application ID is required for adoption record")

            # Create Adoption entity using direct Pydantic model construction
            pet_id_int = int(pet.technical_id or pet.entity_id or "0")
            adoption = Adoption(
                customerId=customer_id,
                petId=pet_id_int,
                storeId=store_id,
                applicationId=application_id,
                adoptionFee=adoption_fee,
                contractSigned=contract_signed,
                microchipTransferred=microchip_transferred,
                vaccinationRecordsProvided=vaccination_records_provided,
                adoptionNotes=adoption_notes,
            )

            # Set adoption date
            adoption.set_adoption_date()

            # Convert Pydantic model to dict for EntityService.save()
            adoption_data = adoption.model_dump(by_alias=True)

            # Save the new Adoption entity
            response = await entity_service.save(
                entity=adoption_data,
                entity_class=Adoption.ENTITY_NAME,
                entity_version=str(Adoption.ENTITY_VERSION),
            )

            # Get the technical ID of the created adoption
            created_adoption_id = response.metadata.id

            self.logger.info(
                f"Created Adoption record {created_adoption_id} for pet {pet.technical_id}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to create adoption record for pet {pet.technical_id}: {str(e)}"
            )
            raise ValueError(f"Failed to create adoption record: {str(e)}")
