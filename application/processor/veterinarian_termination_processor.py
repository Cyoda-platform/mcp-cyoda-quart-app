"""
Veterinarian Termination Processor for Purrfect Pets API.
"""

import logging
from datetime import datetime, timezone

from application.entity.veterinarian.version_1.veterinarian import Veterinarian
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class VeterinarianTerminationProcessor(CyodaProcessor):
    """Processor to handle termination of veterinarian."""

    def __init__(
        self, name: str = "VeterinarianTerminationProcessor", description: str = ""
    ):
        super().__init__(
            name=name, description=description or "Process termination of veterinarian"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process veterinarian termination."""
        try:
            if not isinstance(entity, Veterinarian):
                raise ProcessorError(
                    self.name, f"Expected Veterinarian entity, got {type(entity)}"
                )

            vet = entity

            # Set veterinarian as unavailable
            vet.is_available = False

            # Reassign future appointments
            await self._reassign_future_appointments(vet.vet_id)

            # Revoke system access
            await self._revoke_system_access(vet.vet_id)

            # Archive medical records (no transition)
            await self._archive_medical_records(vet.vet_id)

            # Create termination record
            await self._create_termination_record(vet)

            # Log termination event
            vet.add_metadata("termination_processor", self.name)
            vet.add_metadata(
                "termination_timestamp", datetime.now(timezone.utc).isoformat()
            )
            vet.add_metadata(
                "termination_reason", kwargs.get("reason", "Employment termination")
            )

            logger.info(f"Successfully terminated veterinarian {vet.vet_id}")

            return vet

        except Exception as e:
            logger.exception(f"Failed to terminate veterinarian {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to terminate veterinarian: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Veterinarian)

    async def _reassign_future_appointments(self, vet_id: str) -> None:
        """Reassign future appointments."""
        logger.info(f"Reassigning future appointments for veterinarian {vet_id}")
        # TODO: Implement actual appointment reassignment

    async def _revoke_system_access(self, vet_id: str) -> None:
        """Revoke system access."""
        logger.info(f"Revoking system access for veterinarian {vet_id}")
        # TODO: Implement actual access revocation

    async def _archive_medical_records(self, vet_id: str) -> None:
        """Archive medical records (no transition)."""
        logger.info(f"Archiving medical records for veterinarian {vet_id}")
        # TODO: Update medical records without transition

    async def _create_termination_record(self, vet: Veterinarian) -> None:
        """Create termination record."""
        termination_record = {
            "vet_id": vet.vet_id,
            "vet_name": vet.get_full_name(),
            "license_number": vet.license_number,
            "termination_date": datetime.now(timezone.utc).isoformat(),
        }
        logger.info(f"Termination record created: {termination_record}")
        # TODO: Store termination record
