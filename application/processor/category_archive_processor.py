"""
CategoryArchiveProcessor for Purrfect Pets Application

Archives a category that is no longer needed as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.category.version_1.category import Category
from services.services import get_entity_service


class CategoryArchiveProcessor(CyodaProcessor):
    """
    Processor for archiving Category entities.
    Validates no pets are currently using this category.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CategoryArchiveProcessor",
            description="Archive a category that is no longer needed"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Category entity for archiving.

        Args:
            entity: The Category entity to archive
            **kwargs: Additional processing parameters

        Returns:
            The archived Category entity
        """
        try:
            self.logger.info(
                f"Processing Category archiving for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Category for type-safe operations
            category = cast_entity(entity, Category)

            # Validate no pets are currently using this category
            entity_service = get_entity_service()
            try:
                # Search for pets with this category ID
                from common.service.entity_service import SearchConditionRequest
                
                builder = SearchConditionRequest.builder()
                builder.equals("categoryId", str(category.technical_id))
                search_condition = builder.build()

                pet_results = await entity_service.search(
                    entity_class="Pet",
                    condition=search_condition,
                    entity_version="1"
                )

                # Check if any pets are using this category and are not archived
                active_pets = []
                for pet_result in pet_results:
                    pet_state = getattr(pet_result.metadata, 'state', None)
                    if pet_state != "archived":
                        active_pets.append(pet_result.metadata.id)

                if active_pets:
                    raise ValueError(f"Cannot archive category - {len(active_pets)} pets are still using this category")

                self.logger.info(f"Category {category.technical_id} has no active pets - safe to archive")

            except Exception as e:
                if "Cannot archive category" in str(e):
                    raise e
                self.logger.error(f"Failed to validate pets using this category: {str(e)}")
                raise ValueError(f"Category validation failed: {str(e)}")

            # Set archive date and update timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            category.updated_at = current_time
            
            # Add archive metadata if we had such fields
            if hasattr(category, 'metadata') and category.metadata:
                category.metadata['archived_at'] = current_time
            else:
                category.metadata = {'archived_at': current_time}

            self.logger.info(f"Category archiving processed successfully for {category.technical_id}")
            return category

        except Exception as e:
            self.logger.error(
                f"Error processing Category archiving for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
