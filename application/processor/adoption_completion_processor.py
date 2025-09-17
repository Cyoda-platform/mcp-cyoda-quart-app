"""
AdoptionCompletionProcessor for Purrfect Pets API

Completes the adoption process and creates an Adoption entity.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.adoption.version_1.adoption import Adoption


class AdoptionCompletionProcessor(CyodaProcessor):
    """
    Processor for Adoption completion that finalizes the adoption process.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AdoptionCompletionProcessor",
            description="Completes the adoption process and finalizes all documentation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Adoption completion according to functional requirements.

        Args:
            entity: The Adoption entity to process (must be in initial state)
            **kwargs: Additional processing parameters

        Returns:
            The processed adoption entity in completed state
        """
        try:
            self.logger.info(
                f"Processing Adoption completion for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Validate all required documentation is complete
            self._validate_adoption_requirements(adoption)

            # Set adoption date to current timestamp
            adoption.set_adoption_date()

            # Validate contract is signed
            if not adoption.contract_signed:
                raise ValueError("Adoption contract must be signed")

            # Validate adoption fee is paid
            if adoption.adoption_fee <= 0:
                raise ValueError("Adoption fee must be paid")

            # Validate microchip transfer if applicable
            if not adoption.microchip_transferred:
                self.logger.warning(
                    f"Microchip not transferred for adoption {adoption.technical_id}"
                )

            # Validate vaccination records provided
            if not adoption.vaccination_records_provided:
                self.logger.warning(
                    f"Vaccination records not provided for adoption {adoption.technical_id}"
                )

            # Create adoption completion record (in a real system)
            # This would update various related entities and create audit trails
            self.logger.info(
                f"Would update pet {adoption.pet_id} status to adopted"
            )

            # Log adoption completion
            self.logger.info(
                f"Adoption {adoption.technical_id} completed successfully for customer {adoption.customer_id}"
            )

            return adoption

        except Exception as e:
            self.logger.error(
                f"Error processing adoption completion {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_adoption_requirements(self, adoption: Adoption) -> None:
        """
        Validate that all adoption requirements are met.

        Args:
            adoption: The Adoption entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Customer ID must be valid
        if adoption.customer_id <= 0:
            raise ValueError("Valid customer ID is required")

        # Pet ID must be valid
        if adoption.pet_id <= 0:
            raise ValueError("Valid pet ID is required")

        # Store ID must be valid
        if adoption.store_id <= 0:
            raise ValueError("Valid store ID is required")

        # Application ID must be valid
        if adoption.application_id <= 0:
            raise ValueError("Valid application ID is required")

        # Adoption fee must be non-negative
        if adoption.adoption_fee < 0:
            raise ValueError("Adoption fee must be non-negative")

        self.logger.debug(f"Adoption requirements validation passed for {adoption.technical_id}")
