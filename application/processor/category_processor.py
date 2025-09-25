"""
CategoryProcessor for Purrfect Pets API Application

Handles the main business logic for processing Category instances.
Minimal processing as categories are simple entities.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.category.version_1.category import Category


class CategoryProcessor(CyodaProcessor):
    """
    Processor for Category entity that handles minimal business logic.
    Categories are simple entities that mainly need basic processing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CategoryProcessor",
            description="Processes Category instances with minimal business logic",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Category with minimal business logic.

        Args:
            entity: The Category to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with basic enriched data
        """
        try:
            self.logger.info(
                f"Processing Category {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Enrich category with minimal processed data
            processed_data = self._create_processed_data(category)
            category.processed_data = processed_data

            # Log processing completion
            self.logger.info(
                f"Category {category.technical_id} processed successfully"
            )

            return category

        except Exception as e:
            self.logger.error(
                f"Error processing category {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_processed_data(self, category: Category) -> Dict[str, Any]:
        """
        Create minimal processed data for the category.

        Args:
            category: The Category to process

        Returns:
            Dictionary containing processed data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        processing_id = str(uuid.uuid4())

        # Create minimal processed data
        processed_data: Dict[str, Any] = {
            "processed_at": current_timestamp,
            "processing_id": processing_id,
            "processing_status": "COMPLETED",
            "normalized_name": category.name.upper(),
            "has_description": bool(category.description),
        }

        return processed_data
