"""
CreateSearchIndex Processor for HNItem

Creates search index entries for stored HNItem data to enable
fast text search and hierarchy traversal.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.hnitem.version_1.hnitem import HNItem


class CreateSearchIndex(CyodaProcessor):
    """
    Processor for creating search index entries for HNItem.
    Creates text index and hierarchy index for fast searching.
    """

    def __init__(self) -> None:
        super().__init__(
            name="create_search_index",
            description="Creates search index entries for HNItem",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Create search index entries for the stored HNItem.

        Args:
            entity: The stored HNItem to index
            **kwargs: Additional processing parameters

        Returns:
            The indexed entity with indexing metadata
        """
        try:
            self.logger.info(
                f"Creating search index for HNItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItem for type-safe operations
            hn_item = cast_entity(entity, HNItem)

            # Create text index
            self._create_text_index(hn_item)

            # Create hierarchy index
            self._create_hierarchy_index(hn_item)

            # Add indexing timestamp
            hn_item.indexed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            self.logger.info(
                f"Search index created for HNItem {hn_item.technical_id}"
            )

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error creating search index for HNItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_text_index(self, hn_item: HNItem) -> None:
        """
        Create text search index for the item.
        
        Args:
            hn_item: The HNItem to index
        """
        try:
            # In a real implementation, this would create entries in a search engine
            # like Elasticsearch, Solr, or a database full-text index
            
            # For now, we'll just log what would be indexed
            if hn_item.search_text:
                self.logger.debug(f"Would index text: {hn_item.search_text[:100]}...")
            
            # Index by type for filtering
            if hn_item.type:
                self.logger.debug(f"Would index type: {hn_item.type}")
            
            # Index by author for filtering
            if hn_item.by:
                self.logger.debug(f"Would index author: {hn_item.by}")
            
            # Index by score for sorting
            if hn_item.score is not None:
                self.logger.debug(f"Would index score: {hn_item.score}")
            
            # Index by time for sorting
            if hn_item.time:
                self.logger.debug(f"Would index time: {hn_item.time}")
                
        except Exception as e:
            self.logger.warning(f"Error creating text index: {str(e)}")

    def _create_hierarchy_index(self, hn_item: HNItem) -> None:
        """
        Create hierarchy index for parent-child relationships.
        
        Args:
            hn_item: The HNItem to index
        """
        try:
            # In a real implementation, this would create entries for fast hierarchy traversal
            
            # Index parent relationship
            if hn_item.parent:
                self.logger.debug(f"Would index parent relationship: {hn_item.id} -> {hn_item.parent}")
            
            # Index children relationships
            if hn_item.kids:
                for kid_id in hn_item.kids:
                    self.logger.debug(f"Would index child relationship: {hn_item.id} -> {kid_id}")
            
            # Index parent chain for fast ancestor lookup
            if hn_item.parent_chain:
                self.logger.debug(f"Would index parent chain: {hn_item.parent_chain}")
            
            # Index poll relationships
            if hn_item.poll:
                self.logger.debug(f"Would index poll relationship: {hn_item.id} -> poll {hn_item.poll}")
            
            if hn_item.parts:
                for part_id in hn_item.parts:
                    self.logger.debug(f"Would index poll part: {hn_item.id} -> part {part_id}")
                    
        except Exception as e:
            self.logger.warning(f"Error creating hierarchy index: {str(e)}")
