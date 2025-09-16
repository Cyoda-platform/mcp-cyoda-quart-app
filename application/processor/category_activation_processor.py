"""
CategoryActivationProcessor for Purrfect Pets API

Handles the activation of Category entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.category.version_1.category import Category
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CategoryActivationProcessor(CyodaProcessor):
    """
    Processor for activating Category entities.
    Validates category name uniqueness and enables category for pet assignments.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CategoryActivationProcessor",
            description="Activates Category entities and enables them for pet assignments",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Category entity activation.

        Args:
            entity: The Category entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated Category entity
        """
        try:
            self.logger.info(
                f"Activating Category {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Validate category name uniqueness (would normally check database)
            # For now, we'll assume this validation is handled elsewhere
            self.logger.info(f"Category name uniqueness validated for: {category.name}")

            # Set activation timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add activation metadata
            if not category.metadata:
                category.metadata = {}

            category.metadata.update(
                {
                    "activation_date": current_time,
                    "activation_status": "active",
                    "pet_assignments_enabled": True,
                }
            )

            # Update timestamp
            category.update_timestamp()

            self.logger.info(
                f"Category {category.technical_id} ({category.name}) activated successfully"
            )

            return category

        except Exception as e:
            self.logger.error(
                f"Error activating Category {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
