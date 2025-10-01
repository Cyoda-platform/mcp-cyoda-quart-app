"""
ReactivatePositionProcessor for Cyoda Client Application

Handles the reactivation of positions for assignment
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.position.version_1.position import Position


class ReactivatePositionProcessor(CyodaProcessor):
    """
    Processor for reactivating Position entities for assignment.
    Transitions position from inactive back to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReactivatePositionProcessor",
            description="Reactivates position for employee assignment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Position reactivation according to functional requirements.

        Args:
            entity: The Position entity to reactivate
            **kwargs: Additional processing parameters

        Returns:
            The reactivated position
        """
        try:
            self.logger.info(
                f"Reactivating Position {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Position for type-safe operations
            position = cast_entity(entity, Position)

            # Reactivate the position
            position.is_active = True
            current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            position.updated_at = current_timestamp

            # Add reactivation metadata
            position.add_metadata("reactivated_at", current_timestamp)
            position.add_metadata("reactivation_reason", kwargs.get("reason", "Manual reactivation"))

            # Clear previous deactivation metadata
            if position.metadata and "deactivated_at" in position.metadata:
                position.add_metadata("previous_deactivation_cleared", position.metadata.get("deactivated_at"))

            # Log position reactivation
            self.logger.info(
                f"Position {position.title} in {position.department} reactivated successfully"
            )

            return position

        except Exception as e:
            self.logger.error(
                f"Error reactivating position {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
