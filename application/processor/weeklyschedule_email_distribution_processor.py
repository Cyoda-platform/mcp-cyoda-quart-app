"""
WeeklySchedule Email Distribution Processor for initiating email distribution.
"""

import logging
from typing import Any, Dict, Optional

from application.entity.weeklyschedule.version_1.weeklyschedule import \
    WeeklySchedule
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class WeeklyScheduleEmailDistributionProcessor(CyodaProcessor):
    """Processor to initiate email distribution to all subscribers."""

    def __init__(
        self,
        name: str = "WeeklyScheduleEmailDistributionProcessor",
        description: str = "",
    ):
        super().__init__(
            name=name,
            description=description
            or "Initiates email distribution to all subscribers",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Initiate email distribution."""
        try:
            if not isinstance(entity, WeeklySchedule):
                raise ProcessorError(
                    self.name, f"Expected WeeklySchedule entity, got {type(entity)}"
                )

            # Validate cat fact is available
            if not entity.catFactId:
                raise ProcessorError(
                    self.name, "WeeklySchedule must have catFactId to distribute emails"
                )

            # Get entity service
            entity_service = self._get_entity_service()

            # Get cat fact and trigger distribution
            try:
                catfact_response = await entity_service.get_by_id(
                    str(entity.catFactId), "catfact", "1"
                )

                # Trigger CatFact workflow with distribution transition
                # In a real implementation, this would be handled by the workflow engine
                # For now, we'll update the cat fact to trigger distribution
                await entity_service.update(
                    str(entity.catFactId),
                    catfact_response.data,
                    "catfact",
                    transition="transition_to_sent",
                    entity_version="1",
                )

                # Add distribution metadata
                entity.add_metadata("distribution_initiated_at", entity.updated_at)
                entity.add_metadata("catfact_distributed", entity.catFactId)

            except Exception as e:
                raise ProcessorError(
                    self.name, f"Failed to trigger cat fact distribution: {str(e)}"
                )

            logger.info(f"Initiated email distribution for weekly schedule {entity.id}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to initiate email distribution for weekly schedule {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to initiate email distribution: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, WeeklySchedule)

    def _get_entity_service(self):
        """Get entity service."""
        from service.services import get_entity_service

        return get_entity_service()
