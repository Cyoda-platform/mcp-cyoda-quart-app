"""
CreatePositionProcessor for Cyoda Client Application

Handles the creation and activation of positions
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.position.version_1.position import Position
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CreatePositionProcessor(CyodaProcessor):
    """
    Processor for creating and activating Position entities.
    Initializes position in active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreatePositionProcessor",
            description="Creates and activates position for employee assignment",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Position creation according to functional requirements.

        Args:
            entity: The Position entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed position in active state
        """
        try:
            self.logger.info(
                f"Creating Position {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Position for type-safe operations
            position = cast_entity(entity, Position)

            # Set position as active immediately upon creation
            position.is_active = True
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Update timestamps
            if not position.created_at:
                position.created_at = current_timestamp
            position.updated_at = current_timestamp

            # Validate salary range if provided
            self._validate_salary_range(position)

            # Log position creation
            self.logger.info(
                f"Position {position.title} created successfully in {position.department} department"
            )

            return position

        except Exception as e:
            self.logger.error(
                f"Error creating position {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_salary_range(self, position: Position) -> None:
        """
        Validate the salary range if provided.

        Args:
            position: The position to validate
        """
        if (
            position.salary_range_min is not None
            and position.salary_range_max is not None
        ):
            if position.salary_range_min > position.salary_range_max:
                raise ValueError("Minimum salary cannot be greater than maximum salary")

            if position.salary_range_min < 0 or position.salary_range_max < 0:
                raise ValueError("Salary range values cannot be negative")

        self.logger.debug(
            f"Salary range validation passed for position: {position.title}"
        )
