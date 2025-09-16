"""
TagArchiveProcessor for Purrfect Pets Application

Archives a tag that is no longer used as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.tag.version_1.tag import Tag
from services.services import get_entity_service


class TagArchiveProcessor(CyodaProcessor):
    """
    Processor for archiving Tag entities.
    Validates no pets are currently using this tag.
    """

    def __init__(self) -> None:
        super().__init__(
            name="TagArchiveProcessor",
            description="Archive a tag that is no longer used"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Tag entity for archiving.

        Args:
            entity: The Tag entity to archive
            **kwargs: Additional processing parameters

        Returns:
            The archived Tag entity
        """
        try:
            self.logger.info(
                f"Processing Tag archiving for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Tag for type-safe operations
            tag = cast_entity(entity, Tag)

            # Validate no pets are currently using this tag
            entity_service = get_entity_service()
            try:
                # Search for pets that have this tag ID in their tagIds array
                # Note: This is a simplified search - in a real implementation,
                # we might need more sophisticated array searching
                from common.service.entity_service import SearchConditionRequest
                
                # Get all pets and check their tagIds manually
                # This is not the most efficient approach but works for the requirements
                all_pets = await entity_service.find_all(
                    entity_class="Pet",
                    entity_version="1"
                )

                # Check if any pets are using this tag and are not archived
                pets_using_tag = []
                tag_id_str = str(tag.technical_id)
                
                for pet_result in all_pets:
                    pet_state = getattr(pet_result.metadata, 'state', None)
                    if pet_state != "archived":
                        # Check if this pet has the tag
                        pet_data = pet_result.data
                        tag_ids = []
                        
                        # Handle different possible field names and formats
                        if hasattr(pet_data, 'tag_ids'):
                            tag_ids = pet_data.tag_ids or []
                        elif hasattr(pet_data, 'tagIds'):
                            tag_ids = pet_data.tagIds or []
                        elif isinstance(pet_data, dict):
                            tag_ids = pet_data.get('tagIds', pet_data.get('tag_ids', []))
                        
                        # Convert tag IDs to strings for comparison
                        tag_ids_str = [str(tid) for tid in tag_ids] if tag_ids else []
                        
                        if tag_id_str in tag_ids_str:
                            pets_using_tag.append(pet_result.metadata.id)

                if pets_using_tag:
                    raise ValueError(f"Cannot archive tag - {len(pets_using_tag)} pets are still using this tag")

                self.logger.info(f"Tag {tag.technical_id} is not being used by any active pets - safe to archive")

            except Exception as e:
                if "Cannot archive tag" in str(e):
                    raise e
                self.logger.error(f"Failed to validate pets using this tag: {str(e)}")
                raise ValueError(f"Tag validation failed: {str(e)}")

            # Set archive date
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            # Add archive metadata if we had such fields
            if hasattr(tag, 'metadata') and tag.metadata:
                tag.metadata['archived_at'] = current_time
            else:
                tag.metadata = {'archived_at': current_time}

            self.logger.info(f"Tag archiving processed successfully for {tag.technical_id}")
            return tag

        except Exception as e:
            self.logger.error(
                f"Error processing Tag archiving for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
