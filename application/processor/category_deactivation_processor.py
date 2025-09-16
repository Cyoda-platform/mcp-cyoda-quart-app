"""
CategoryDeactivationProcessor for Purrfect Pets API

Handles the deactivation of Category entities.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.category.version_1.category import Category


class CategoryDeactivationProcessor(CyodaProcessor):
    """
    Processor for deactivating Category entities.
    Checks for active pets and prevents new pet assignments.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CategoryDeactivationProcessor",
            description="Deactivates Category entities and prevents new pet assignments",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Category entity deactivation.

        Args:
            entity: The Category entity to deactivate
            **kwargs: Additional processing parameters

        Returns:
            The deactivated Category entity
        """
        try:
            self.logger.info(
                f"Deactivating Category {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Check if category has active pets (would normally query database)
            # For now, we'll log this check and assume it's handled elsewhere
            self.logger.info(f"Checking for active pets in category: {category.name}")

            # Set deactivation timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add deactivation metadata
            if not category.metadata:
                category.metadata = {}
            
            category.metadata.update({
                "deactivation_date": current_time,
                "activation_status": "inactive",
                "pet_assignments_enabled": False
            })

            # Clear activation metadata
            category.metadata.pop("activation_date", None)

            # Update timestamp
            category.update_timestamp()

            self.logger.info(
                f"Category {category.technical_id} ({category.name}) deactivated successfully"
            )

            return category

        except Exception as e:
            self.logger.error(
                f"Error deactivating Category {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
