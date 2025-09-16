"""
CategoryCreationProcessor for Purrfect Pets Application

Initializes a new category record as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.category.version_1.category import Category
from services.services import get_entity_service


class CategoryCreationProcessor(CyodaProcessor):
    """
    Processor for initializing new Category entities.
    Validates required fields and checks for duplicates.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CategoryCreationProcessor",
            description="Initialize a new category record"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Category entity during creation.

        Args:
            entity: The Category entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed Category entity with initialized data
        """
        try:
            self.logger.info(
                f"Processing Category creation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Validate required fields
            if not category.name or len(category.name.strip()) == 0:
                raise ValueError("Category name is required")

            # Check for duplicate category names
            entity_service = get_entity_service()
            try:
                # Search for existing categories with the same name
                from common.service.entity_service import SearchConditionRequest
                
                builder = SearchConditionRequest.builder()
                builder.equals("name", category.name.strip())
                search_condition = builder.build()

                existing_categories = await entity_service.search(
                    entity_class="Category",
                    condition=search_condition,
                    entity_version="1"
                )

                # Check if any existing category has the same name and is not archived
                for existing_category in existing_categories:
                    existing_state = getattr(existing_category.metadata, 'state', None)
                    if existing_state != "archived":
                        raise ValueError(f"Category with name '{category.name}' already exists")

            except Exception as e:
                if "already exists" in str(e):
                    raise e
                self.logger.warning(f"Could not check for duplicate category names: {str(e)}")
                # Continue processing - duplicate check failure shouldn't prevent creation

            # Set default description if not provided
            if not category.description:
                category.description = f"Category for {category.name}"

            # Set timestamps
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            category.created_at = current_time
            category.updated_at = current_time

            self.logger.info(f"Category creation processed successfully for {category.technical_id}")
            return category

        except Exception as e:
            self.logger.error(
                f"Error processing Category creation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
