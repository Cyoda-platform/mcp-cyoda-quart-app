"""
TagCreationProcessor for Purrfect Pets Application

Initializes a new tag record as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.tag.version_1.tag import Tag
from services.services import get_entity_service


class TagCreationProcessor(CyodaProcessor):
    """
    Processor for initializing new Tag entities.
    Validates required fields and checks for duplicates.
    """

    def __init__(self) -> None:
        super().__init__(
            name="TagCreationProcessor",
            description="Initialize a new tag record"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Tag entity during creation.

        Args:
            entity: The Tag entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed Tag entity with initialized data
        """
        try:
            self.logger.info(
                f"Processing Tag creation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Tag for type-safe operations
            tag = cast_entity(entity, Tag)

            # Validate required fields
            if not tag.name or len(tag.name.strip()) == 0:
                raise ValueError("Tag name is required")

            # Check for duplicate tag names
            entity_service = get_entity_service()
            try:
                # Search for existing tags with the same name
                from common.service.entity_service import SearchConditionRequest
                
                builder = SearchConditionRequest.builder()
                builder.equals("name", tag.name.strip())
                search_condition = builder.build()

                existing_tags = await entity_service.search(
                    entity_class="Tag",
                    condition=search_condition,
                    entity_version="1"
                )

                # Check if any existing tag has the same name and is not archived
                for existing_tag in existing_tags:
                    existing_state = getattr(existing_tag.metadata, 'state', None)
                    if existing_state != "archived":
                        raise ValueError(f"Tag with name '{tag.name}' already exists")

            except Exception as e:
                if "already exists" in str(e):
                    raise e
                self.logger.warning(f"Could not check for duplicate tag names: {str(e)}")
                # Continue processing - duplicate check failure shouldn't prevent creation

            # Set default color if not provided
            if not tag.color:
                # Default colors for common tag types
                tag_name_lower = tag.name.lower()
                if "friendly" in tag_name_lower:
                    tag.color = "#4CAF50"  # Green
                elif "aggressive" in tag_name_lower or "caution" in tag_name_lower:
                    tag.color = "#F44336"  # Red
                elif "playful" in tag_name_lower or "active" in tag_name_lower:
                    tag.color = "#FF9800"  # Orange
                elif "calm" in tag_name_lower or "quiet" in tag_name_lower:
                    tag.color = "#2196F3"  # Blue
                else:
                    tag.color = "#9E9E9E"  # Gray (default)

            # Set timestamps
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            tag.created_at = current_time

            self.logger.info(f"Tag creation processed successfully for {tag.technical_id}")
            return tag

        except Exception as e:
            self.logger.error(
                f"Error processing Tag creation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
