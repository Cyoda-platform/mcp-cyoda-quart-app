"""
FinalizeStorageProcessor for Cyoda Client Application

Finalizes storage and performs post-storage operations for HN items.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.hnitem.version_1.hnitem import HnItem


class FinalizeStorageProcessor(CyodaProcessor):
    """
    Processor for finalizing storage and performing post-storage operations.
    """

    def __init__(self) -> None:
        super().__init__(
            name="finalize_storage_processor",
            description="Finalizes storage and performs post-storage operations for HN items",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Finalize storage and perform post-storage operations.

        Args:
            entity: The successfully stored HnItem
            **kwargs: Additional processing parameters

        Returns:
            The finalized entity
        """
        try:
            self.logger.info(
                f"Finalizing storage for HnItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Perform post-storage operations
            await self._update_search_index(hn_item)
            await self._update_statistics(hn_item)
            await self._trigger_notifications(hn_item)

            # Mark processing as completed
            hn_item.processing_completed_at = int(datetime.now(timezone.utc).timestamp())
            hn_item.status = "active"

            self.logger.info(
                f"Storage finalization completed for HnItem {hn_item.id}"
            )

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error finalizing storage for HnItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _update_search_index(self, item: HnItem) -> None:
        """Update search index for the item"""
        try:
            # Log search index update (in a real implementation, this would update a search engine)
            searchable_content = []
            
            if item.title:
                searchable_content.append(f"title:{item.title}")
            if item.text:
                searchable_content.append(f"text:{item.text[:100]}...")  # Truncate for logging
            if item.by:
                searchable_content.append(f"author:{item.by}")
            
            self.logger.info(
                f"Updated search index for HnItem {item.id}: {'; '.join(searchable_content)}"
            )
            
        except Exception as e:
            self.logger.warning(f"Error updating search index for item {item.id}: {str(e)}")

    async def _update_statistics(self, item: HnItem) -> None:
        """Update item statistics"""
        try:
            # Log statistics update (in a real implementation, this would update metrics)
            self.logger.info(
                f"Updated statistics for item type {item.type}, source {item.source}"
            )
            
            # Log additional metrics based on item type
            if item.type == "story" and item.score:
                self.logger.info(f"Story {item.id} has score {item.score}")
            elif item.type == "comment" and item.parent:
                self.logger.info(f"Comment {item.id} added to parent {item.parent}")
            elif item.type == "poll" and item.parts:
                self.logger.info(f"Poll {item.id} has {len(item.parts)} options")
                
        except Exception as e:
            self.logger.warning(f"Error updating statistics for item {item.id}: {str(e)}")

    async def _trigger_notifications(self, item: HnItem) -> None:
        """Trigger notifications if needed"""
        try:
            # Trigger notifications based on source and type
            if item.source == "firebase_api":
                self.logger.info(f"New item {item.id} from Firebase API: {item.type}")
            elif item.source == "bulk_upload":
                self.logger.info(f"Bulk uploaded item {item.id} processed: {item.type}")
            elif item.source == "manual_post":
                self.logger.info(f"Manually posted item {item.id} processed: {item.type}")
                
            # Special notifications for high-scoring stories
            if item.type == "story" and item.score and item.score > 100:
                self.logger.info(f"High-scoring story detected: {item.id} with score {item.score}")
                
        except Exception as e:
            self.logger.warning(f"Error triggering notifications for item {item.id}: {str(e)}")
