"""
SubmitApplicationProcessor for Purrfect Pets Application

Handles submission of new adoption applications.
Processes new adoption application and reserves the pet.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.adoption.version_1.adoption import Adoption
from services.services import get_entity_service


class SubmitApplicationProcessor(CyodaProcessor):
    """
    Processor for submitting Adoption applications.
    Processes new adoption application and reserves the pet.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubmitApplicationProcessor",
            description="Process new adoption application and reserve pet",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Submit the Adoption application according to functional requirements.

        Args:
            entity: The Adoption entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed adoption application
        """
        try:
            self.logger.info(
                f"Submitting adoption application {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Validate adoption application
            self._validate_adoption_application(adoption)

            # Process the application
            self._process_adoption_application(adoption)

            # Reserve the pet (update pet entity)
            await self._reserve_pet_for_adoption(adoption)

            # Notify staff (simulated)
            self._notify_staff_new_application(adoption)

            self.logger.info(
                f"Adoption application {adoption.technical_id} submitted successfully"
            )

            return adoption

        except Exception as e:
            self.logger.error(
                f"Error submitting adoption application {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_adoption_application(self, adoption: Adoption) -> None:
        """
        Validate adoption application data.

        Args:
            adoption: The Adoption entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Basic validation - Pydantic handles most field validation
        if not adoption.pet_id or len(adoption.pet_id.strip()) == 0:
            raise ValueError("Pet ID is required for adoption application")

        if not adoption.owner_id or len(adoption.owner_id.strip()) == 0:
            raise ValueError("Owner ID is required for adoption application")

        if not adoption.notes or len(adoption.notes.strip()) == 0:
            raise ValueError("Notes are required for adoption application")

        if adoption.fee_paid < 0:
            raise ValueError("Fee paid cannot be negative")

        self.logger.info(f"Adoption application validation passed for pet {adoption.pet_id}")

    def _process_adoption_application(self, adoption: Adoption) -> None:
        """
        Process the adoption application according to functional requirements.

        Args:
            adoption: The Adoption entity to process
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Ensure application_date is set
        if not adoption.application_date:
            adoption.application_date = current_timestamp

        # Add processing metadata
        adoption.add_metadata("status", "pending")
        adoption.add_metadata("submitted_date", current_timestamp)
        adoption.add_metadata("submitted_by", "SubmitApplicationProcessor")

        self.logger.info(
            f"Adoption application for pet {adoption.pet_id} processed on {current_timestamp}"
        )

    async def _reserve_pet_for_adoption(self, adoption: Adoption) -> None:
        """
        Reserve the pet for this adoption application.

        Args:
            adoption: The Adoption entity with pet to reserve
        """
        try:
            entity_service = get_entity_service()

            # Get the pet entity
            pet_response = await entity_service.get_by_id(
                entity_id=adoption.pet_id,
                entity_class="Pet",
                entity_version="1"
            )

            if pet_response and pet_response.data:
                # Update pet with adoption reference
                pet_data = pet_response.data
                if hasattr(pet_data, 'model_dump'):
                    pet_dict = pet_data.model_dump(by_alias=True)
                else:
                    pet_dict = pet_data

                # Set adoption_id reference
                pet_dict["adoption_id"] = adoption.technical_id or adoption.entity_id

                # Update the pet with transition to reserve it
                await entity_service.update(
                    entity_id=adoption.pet_id,
                    entity=pet_dict,
                    entity_class="Pet",
                    transition="reserve_pet",
                    entity_version="1"
                )

                self.logger.info(f"Pet {adoption.pet_id} reserved for adoption {adoption.technical_id}")
            else:
                self.logger.warning(f"Pet {adoption.pet_id} not found for reservation")

        except Exception as e:
            self.logger.error(f"Failed to reserve pet {adoption.pet_id}: {str(e)}")
            # Don't raise exception as the adoption application itself is valid

    def _notify_staff_new_application(self, adoption: Adoption) -> None:
        """
        Notify staff about new adoption application (simulated).

        Args:
            adoption: The Adoption entity to notify about
        """
        # Simulate notifying staff
        self.logger.info(
            f"Staff notified about new adoption application {adoption.technical_id} for pet {adoption.pet_id}"
        )
        
        # Add metadata to track notification
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        adoption.add_metadata("staff_notified", current_timestamp)
