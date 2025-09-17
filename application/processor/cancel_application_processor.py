"""
CancelApplicationProcessor for Purrfect Pets Application

Handles cancellation of adoption applications.
Cancels adoption applications and releases reserved pets.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.adoption.version_1.adoption import Adoption
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class CancelApplicationProcessor(CyodaProcessor):
    """
    Processor for cancelling Adoption applications.
    Cancels adoption applications and releases reserved pets.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CancelApplicationProcessor",
            description="Cancel adoption application and release reserved pet",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Cancel the Adoption application according to functional requirements.

        Args:
            entity: The Adoption entity to cancel
            **kwargs: Additional processing parameters

        Returns:
            The cancelled adoption application
        """
        try:
            self.logger.info(
                f"Cancelling adoption application {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Validate adoption can be cancelled
            self._validate_adoption_for_cancellation(adoption)

            # Cancel the application
            self._cancel_adoption_application(adoption)

            # Release the reserved pet
            await self._release_reserved_pet(adoption)

            # Update owner records
            await self._update_owner_records_for_cancellation(adoption)

            self.logger.info(
                f"Adoption application {adoption.technical_id} cancelled successfully"
            )

            return adoption

        except Exception as e:
            self.logger.error(
                f"Error cancelling adoption application {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_adoption_for_cancellation(self, adoption: Adoption) -> None:
        """
        Validate that adoption application can be cancelled.

        Args:
            adoption: The Adoption entity to validate

        Raises:
            ValueError: If adoption cannot be cancelled
        """
        if adoption.is_completed():
            raise ValueError(
                f"Cannot cancel completed adoption (current state: {adoption.state})"
            )

        if adoption.is_cancelled():
            raise ValueError(
                f"Adoption is already cancelled (current state: {adoption.state})"
            )

        # Can cancel pending or approved adoptions
        if not (adoption.is_pending() or adoption.is_approved()):
            raise ValueError(
                f"Adoption cannot be cancelled from state: {adoption.state}"
            )

        self.logger.info("Adoption validation passed for cancellation")

    def _cancel_adoption_application(self, adoption: Adoption) -> None:
        """
        Cancel the adoption application according to functional requirements.

        Args:
            adoption: The Adoption entity to cancel
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Add cancellation metadata
        adoption.add_metadata("status", "cancelled")
        adoption.add_metadata("cancelled_date", current_timestamp)
        adoption.add_metadata("cancelled_by", "CancelApplicationProcessor")

        # Add cancellation note
        adoption.add_note(f"Application cancelled on {current_timestamp}")

        self.logger.info(
            f"Adoption application for pet {adoption.pet_id} cancelled on {current_timestamp}"
        )

    async def _release_reserved_pet(self, adoption: Adoption) -> None:
        """
        Release the reserved pet back to available status.

        Args:
            adoption: The Adoption entity with pet to release
        """
        try:
            entity_service = get_entity_service()

            # Get the pet entity
            pet_response = await entity_service.get_by_id(
                entity_id=adoption.pet_id, entity_class="Pet", entity_version="1"
            )

            if pet_response and pet_response.data:
                # Update pet to clear adoption reference
                pet_data = pet_response.data
                if hasattr(pet_data, "model_dump"):
                    pet_dict = pet_data.model_dump(by_alias=True)
                else:
                    pet_dict = pet_data if isinstance(pet_data, dict) else pet_data.__dict__

                # Clear adoption_id reference
                pet_dict["adoption_id"] = None

                # Update the pet with transition to cancel reservation
                await entity_service.update(
                    entity_id=adoption.pet_id,
                    entity=pet_dict,
                    entity_class="Pet",
                    transition="cancel_reservation",
                    entity_version="1",
                )

                self.logger.info(f"Pet {adoption.pet_id} released from reservation")
            else:
                self.logger.warning(f"Pet {adoption.pet_id} not found for release")

        except Exception as e:
            self.logger.error(f"Failed to release pet {adoption.pet_id}: {str(e)}")
            # Don't raise exception as the cancellation itself is valid

    async def _update_owner_records_for_cancellation(self, adoption: Adoption) -> None:
        """
        Update owner records to remove cancelled adoption.

        Args:
            adoption: The Adoption entity with owner to update
        """
        try:
            entity_service = get_entity_service()

            # Get the owner entity
            owner_response = await entity_service.get_by_id(
                entity_id=adoption.owner_id, entity_class="Owner", entity_version="1"
            )

            if owner_response and owner_response.data:
                # Update owner to remove adoption reference
                owner_data = owner_response.data
                if hasattr(owner_data, "model_dump"):
                    owner_dict = owner_data.model_dump(by_alias=True)
                else:
                    owner_dict = owner_data if isinstance(owner_data, dict) else owner_data.__dict__

                # Remove adoption from lists if present
                adoption_id = adoption.technical_id or adoption.entity_id
                if (
                    "adoption_ids" in owner_dict
                    and adoption_id in owner_dict["adoption_ids"]
                ):
                    owner_dict["adoption_ids"].remove(adoption_id)

                # Update the owner (no transition needed)
                await entity_service.update(
                    entity_id=adoption.owner_id,
                    entity=owner_dict,
                    entity_class="Owner",
                    entity_version="1",
                )

                self.logger.info(
                    f"Owner {adoption.owner_id} records updated for cancellation"
                )
            else:
                self.logger.warning(
                    f"Owner {adoption.owner_id} not found for record update"
                )

        except Exception as e:
            self.logger.error(
                f"Failed to update owner {adoption.owner_id} records: {str(e)}"
            )
            # Don't raise exception as the cancellation itself is valid
