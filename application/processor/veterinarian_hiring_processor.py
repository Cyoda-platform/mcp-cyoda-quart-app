"""
Veterinarian Hiring Processor for Purrfect Pets API.
"""

import logging
from datetime import datetime, timezone

from application.entity.veterinarian.version_1.veterinarian import Veterinarian
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class VeterinarianHiringProcessor(CyodaProcessor):
    """Processor to handle hiring of a new veterinarian."""

    def __init__(
        self, name: str = "VeterinarianHiringProcessor", description: str = ""
    ):
        super().__init__(
            name=name, description=description or "Process hiring of a new veterinarian"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process veterinarian hiring."""
        try:
            if not isinstance(entity, Veterinarian):
                raise ProcessorError(
                    self.name, f"Expected Veterinarian entity, got {type(entity)}"
                )

            vet = entity

            # Validate required fields
            self._validate_required_fields(vet)

            # Check duplicate license
            await self._check_duplicate_license(vet.license_number)

            # Set hire date if not already set
            if not vet.hire_date:
                vet.hire_date = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            # Set initial availability to false (needs verification first)
            vet.is_available = False

            # Generate unique vet_id if not provided
            if not vet.vet_id:
                vet.vet_id = f"VET-{vet.entity_id[:8].upper()}"

            # Create employee record
            await self._create_employee_record(vet)

            # Log hiring event
            vet.add_metadata("hiring_processor", self.name)
            vet.add_metadata("hiring_timestamp", datetime.now(timezone.utc).isoformat())

            logger.info(
                f"Successfully hired veterinarian {vet.vet_id} with license {vet.license_number}"
            )

            return vet

        except Exception as e:
            logger.exception(f"Failed to hire veterinarian {entity.entity_id}")
            raise ProcessorError(self.name, f"Failed to hire veterinarian: {str(e)}", e)

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Veterinarian)

    def _validate_required_fields(self, vet: Veterinarian) -> None:
        """Validate required fields."""
        if not vet.first_name or not vet.first_name.strip():
            raise ValueError("First name is required")
        if not vet.last_name or not vet.last_name.strip():
            raise ValueError("Last name is required")
        if not vet.license_number or not vet.license_number.strip():
            raise ValueError("License number is required")

    async def _check_duplicate_license(self, license_number: str) -> None:
        """Check for duplicate license."""
        logger.debug(f"Checking for duplicate license: {license_number}")
        # TODO: Implement actual duplicate check

    async def _create_employee_record(self, vet: Veterinarian) -> None:
        """Create employee record."""
        logger.info(f"Creating employee record for veterinarian {vet.vet_id}")
        # TODO: Implement actual employee record creation
