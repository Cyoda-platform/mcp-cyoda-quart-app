"""
Veterinarian Unavailability Processor for Purrfect Pets API.
"""

import logging
from datetime import datetime, timezone

from application.entity.veterinarian.version_1.veterinarian import Veterinarian
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class VeterinarianUnavailabilityProcessor(CyodaProcessor):
    """Processor to mark veterinarian as temporarily unavailable."""

    def __init__(
        self, name: str = "VeterinarianUnavailabilityProcessor", description: str = ""
    ):
        super().__init__(
            name=name,
            description=description or "Mark veterinarian as temporarily unavailable",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process veterinarian unavailability."""
        try:
            if not isinstance(entity, Veterinarian):
                raise ProcessorError(
                    self.name, f"Expected Veterinarian entity, got {type(entity)}"
                )

            vet = entity

            # Set veterinarian as unavailable
            vet.is_available = False

            # Reschedule future appointments
            await self._reschedule_future_appointments(vet.vet_id)

            # Notify affected owners
            await self._notify_affected_owners(vet.vet_id)

            # Update schedule availability
            await self._update_schedule_availability(vet.vet_id, False)

            # Log unavailability event
            vet.add_metadata("unavailability_processor", self.name)
            vet.add_metadata(
                "unavailability_timestamp", datetime.now(timezone.utc).isoformat()
            )
            vet.add_metadata(
                "unavailability_reason",
                kwargs.get("reason", "Temporary unavailability"),
            )

            logger.info(f"Marked veterinarian {vet.vet_id} as unavailable")

            return vet

        except Exception as e:
            logger.exception(
                f"Failed to mark veterinarian unavailable {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to mark veterinarian unavailable: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Veterinarian)

    async def _reschedule_future_appointments(self, vet_id: str) -> None:
        """Reschedule future appointments."""
        logger.info(f"Rescheduling future appointments for veterinarian {vet_id}")
        # TODO: Implement actual appointment rescheduling

    async def _notify_affected_owners(self, vet_id: str) -> None:
        """Notify affected owners."""
        logger.info(f"Notifying affected owners for veterinarian {vet_id}")
        # TODO: Implement actual owner notification

    async def _update_schedule_availability(self, vet_id: str, available: bool) -> None:
        """Update schedule availability."""
        logger.info(
            f"Updating schedule availability for veterinarian {vet_id}: {available}"
        )
        # TODO: Implement actual schedule update
