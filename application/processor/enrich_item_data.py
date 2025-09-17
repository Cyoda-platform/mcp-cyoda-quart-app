"""
EnrichItemData Processor for HNItem

Enriches HNItem with metadata and resolves relationships
after validation is complete.
"""

import logging
from datetime import datetime, timezone
from typing import Any, List

from application.entity.hnitem.version_1.hnitem import HNItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class EnrichItemData(CyodaProcessor):
    """
    Processor for enriching HNItem with metadata and relationships.
    Adds processed timestamp, search text, and parent chain information.
    """

    def __init__(self) -> None:
        super().__init__(
            name="enrich_item_data",
            description="Enriches HNItem with metadata and resolves relationships",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Enrich the HNItem with metadata and relationship information.

        Args:
            entity: The validated HNItem to enrich
            **kwargs: Additional processing parameters

        Returns:
            The enriched entity with metadata
        """
        try:
            self.logger.info(
                f"Enriching HNItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItem for type-safe operations
            hn_item = cast_entity(entity, HNItem)

            # Add processed timestamp
            hn_item.processed_time = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Create search text by combining title and text
            hn_item.search_text = self._combine_title_and_text(hn_item)

            # Build parent chain for hierarchy traversal
            if hn_item.parent:
                hn_item.parent_chain = await self._build_parent_chain(hn_item.parent)
            else:
                hn_item.parent_chain = []

            self.logger.info(f"HNItem {hn_item.technical_id} enriched successfully")

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error enriching HNItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _combine_title_and_text(self, hn_item: HNItem) -> str:
        """
        Combine title and text fields for search indexing.

        Args:
            hn_item: The HNItem to process

        Returns:
            Combined searchable text
        """
        parts = []

        if hn_item.title:
            # Remove HTML tags for search (simple approach)
            clean_title = self._strip_html_tags(hn_item.title)
            parts.append(clean_title)

        if hn_item.text:
            # Remove HTML tags for search (simple approach)
            clean_text = self._strip_html_tags(hn_item.text)
            parts.append(clean_text)

        if hn_item.by:
            parts.append(f"by:{hn_item.by}")

        if hn_item.url:
            parts.append(f"url:{hn_item.url}")

        return " ".join(parts)

    def _strip_html_tags(self, html_text: str) -> str:
        """
        Simple HTML tag removal for search text.

        Args:
            html_text: Text that may contain HTML tags

        Returns:
            Text with HTML tags removed
        """
        import re

        # Simple regex to remove HTML tags
        clean_text = re.sub(r"<[^>]+>", "", html_text)
        # Replace multiple whitespace with single space
        clean_text = re.sub(r"\s+", " ", clean_text)
        return clean_text.strip()

    async def _build_parent_chain(self, parent_id: int) -> List[int]:
        """
        Build the parent chain for hierarchy traversal.

        Args:
            parent_id: The immediate parent ID

        Returns:
            List of parent IDs from immediate parent to root
        """
        try:
            entity_service = get_entity_service()
            parent_chain = [parent_id]

            # Look up the parent item to continue the chain
            # Note: This is a simplified implementation
            # In a real system, you might want to limit depth or use caching
            current_parent_id = parent_id
            max_depth = 10  # Prevent infinite loops
            depth = 0

            while current_parent_id and depth < max_depth:
                try:
                    # Try to find the parent item
                    # This is a simplified approach - in practice you might need
                    # to search by the HN item ID field rather than entity ID
                    parent_results = await entity_service.search(
                        entity_class=HNItem.ENTITY_NAME,
                        condition=entity_service.SearchConditionRequest.builder()
                        .equals("id", str(current_parent_id))
                        .build(),
                        entity_version=str(HNItem.ENTITY_VERSION),
                    )

                    if parent_results and len(parent_results) > 0:
                        parent_item = cast_entity(parent_results[0].data, HNItem)
                        if (
                            parent_item.parent
                            and parent_item.parent not in parent_chain
                        ):
                            parent_chain.append(parent_item.parent)
                            current_parent_id = parent_item.parent
                        else:
                            break
                    else:
                        break

                except Exception as e:
                    self.logger.warning(
                        f"Could not resolve parent {current_parent_id}: {str(e)}"
                    )
                    break

                depth += 1

            return parent_chain

        except Exception as e:
            self.logger.warning(
                f"Error building parent chain for {parent_id}: {str(e)}"
            )
            return [parent_id]  # Return at least the immediate parent
