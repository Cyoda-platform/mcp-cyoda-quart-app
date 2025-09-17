"""
CompleteAdoptionProcessor for Adoption entities in Purrfect Pets Application

Handles completion of approved adoption applications.
Finalizes the adoption process and updates related entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.adoption.version_1.adoption import Adoption
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class CompleteAdoptionProcessor(CyodaProcessor):
    """
    Processor for completing Adoption applications.
    Finalizes the adoption process and updates related entities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CompleteAdoptionProcessor",
            description="Complete the adoption process and finalize all entities",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Complete the Adoption according to functional requirements.

        Args:
            entity: The Adoption entity to complete
            **kwargs: Additional processing parameters

        Returns:
            The completed adoption
        """
        try:
            self.logger.info(
                f"Completing adoption {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Validate adoption can be completed
            self._validate_adoption_for_completion(adoption)

            # Complete the adoption
            self._complete_adoption(adoption)

            # Finalize pet adoption
            await self._finalize_pet_adoption(adoption)

            # Update owner records
            await self._update_owner_records(adoption)

            # Process payment (simulated)
            self._process_payment(adoption)

            self.logger.info(f"Adoption {adoption.technical_id} completed successfully")

            return adoption

        except Exception as e:
            self.logger.error(
                f"Error completing adoption {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_adoption_for_completion(self, adoption: Adoption) -> None:
        """
        Validate that adoption can be completed.

        Args:
            adoption: The Adoption entity to validate

        Raises:
            ValueError: If adoption cannot be completed
        """
        if not adoption.is_approved():
            raise ValueError(
                f"Adoption is not approved (current state: {adoption.state})"
            )

        # Validate required fields
        if not adoption.pet_id or len(adoption.pet_id.strip()) == 0:
            raise ValueError("Pet ID is required for completion")

        if not adoption.owner_id or len(adoption.owner_id.strip()) == 0:
            raise ValueError("Owner ID is required for completion")

        self.logger.info("Adoption validation passed for completion")

    def _complete_adoption(self, adoption: Adoption) -> None:
        """
        Complete the adoption according to functional requirements.

        Args:
            adoption: The Adoption entity to complete
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Set completion data
        adoption.complete_adoption()  # This sets adoption_date

        # Add completion metadata
        adoption.add_metadata("status", "completed")
        adoption.add_metadata("completed_date", current_timestamp)
        adoption.add_metadata("completed_by", "CompleteAdoptionProcessor")

        self.logger.info(
            f"Adoption for pet {adoption.pet_id} completed on {current_timestamp}"
        )

    async def _finalize_pet_adoption(self, adoption: Adoption) -> None:
        """
        Finalize pet adoption by updating pet entity.

        Args:
            adoption: The Adoption entity with pet to finalize
        """
        try:
            entity_service = get_entity_service()

            # Get the pet entity
            pet_response = await entity_service.get_by_id(
                entity_id=adoption.pet_id, entity_class="Pet", entity_version="1"
            )

            if pet_response and pet_response.data:
                # Update pet with owner reference
                pet_data = pet_response.data
                if hasattr(pet_data, "model_dump"):
                    pet_dict = pet_data.model_dump(by_alias=True)
                else:
                    pet_dict = pet_data if isinstance(pet_data, dict) else pet_data.__dict__

                # Set owner_id reference
                pet_dict["owner_id"] = adoption.owner_id

                # Update the pet with transition to complete adoption
                await entity_service.update(
                    entity_id=adoption.pet_id,
                    entity=pet_dict,
                    entity_class="Pet",
                    transition="complete_adoption",
                    entity_version="1",
                )

                self.logger.info(
                    f"Pet {adoption.pet_id} adoption finalized with owner {adoption.owner_id}"
                )
            else:
                self.logger.warning(f"Pet {adoption.pet_id} not found for finalization")

        except Exception as e:
            self.logger.error(
                f"Failed to finalize pet {adoption.pet_id} adoption: {str(e)}"
            )
            # Don't raise exception as the adoption completion itself is valid

    async def _update_owner_records(self, adoption: Adoption) -> None:
        """
        Update owner records with new pet and adoption.

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
                # Update owner with pet and adoption references
                owner_data = owner_response.data
                if hasattr(owner_data, "model_dump"):
                    owner_dict = owner_data.model_dump(by_alias=True)
                else:
                    owner_dict = owner_data if isinstance(owner_data, dict) else owner_data.__dict__

                # Add pet and adoption to lists
                if "pet_ids" not in owner_dict:
                    owner_dict["pet_ids"] = []
                if "adoption_ids" not in owner_dict:
                    owner_dict["adoption_ids"] = []

                if adoption.pet_id not in owner_dict["pet_ids"]:
                    owner_dict["pet_ids"].append(adoption.pet_id)

                adoption_id = adoption.technical_id or adoption.entity_id
                if adoption_id not in owner_dict["adoption_ids"]:
                    owner_dict["adoption_ids"].append(adoption_id)

                # Update the owner (no transition needed)
                await entity_service.update(
                    entity_id=adoption.owner_id,
                    entity=owner_dict,
                    entity_class="Owner",
                    entity_version="1",
                )

                self.logger.info(
                    f"Owner {adoption.owner_id} records updated with pet {adoption.pet_id}"
                )
            else:
                self.logger.warning(
                    f"Owner {adoption.owner_id} not found for record update"
                )

        except Exception as e:
            self.logger.error(
                f"Failed to update owner {adoption.owner_id} records: {str(e)}"
            )
            # Don't raise exception as the adoption completion itself is valid

    def _process_payment(self, adoption: Adoption) -> None:
        """
        Process payment for the adoption (simulated).

        Args:
            adoption: The Adoption entity to process payment for
        """
        # Simulate payment processing
        self.logger.info(
            f"Payment of ${adoption.fee_paid} processed for adoption {adoption.technical_id}"
        )

        # Add metadata to track payment processing
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        adoption.add_metadata("payment_processed", current_timestamp)
        adoption.add_metadata("payment_amount", adoption.fee_paid)
