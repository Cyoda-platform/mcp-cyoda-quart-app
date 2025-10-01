"""
DeactivatePositionProcessor for Cyoda Client Application

Handles the deactivation of positions from assignment
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.position.version_1.position import Position
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class DeactivatePositionProcessor(CyodaProcessor):
    """
    Processor for deactivating Position entities from assignment.
    Transitions position from active to inactive state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DeactivatePositionProcessor",
            description="Deactivates position from employee assignment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Position deactivation according to functional requirements.

        Args:
            entity: The Position entity to deactivate
            **kwargs: Additional processing parameters

        Returns:
            The deactivated position
        """
        try:
            self.logger.info(
                f"Deactivating Position {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Position for type-safe operations
            position = cast_entity(entity, Position)

            # Deactivate the position
            position.is_active = False
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            position.updated_at = current_timestamp

            # Add deactivation metadata
            position.add_metadata("deactivated_at", current_timestamp)
            position.add_metadata(
                "deactivation_reason", kwargs.get("reason", "Manual deactivation")
            )

            # Log position deactivation
            self.logger.info(
                f"Position {position.title} in {position.department} deactivated successfully"
            )

            # Note: The ValidateNoActiveEmployees criterion should have already
            # verified that no active employees are assigned to this position

            return position

        except Exception as e:
            self.logger.error(
                f"Error deactivating position {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
