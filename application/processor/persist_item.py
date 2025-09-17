"""
PersistItem Processor for HNItem

Handles the persistence of enriched HNItem data to the database.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.hnitem.version_1.hnitem import HNItem


class PersistItem(CyodaProcessor):
    """
    Processor for persisting enriched HNItem data.
    Marks the item as stored and adds storage metadata.
    """

    def __init__(self) -> None:
        super().__init__(
            name="persist_item",
            description="Persists enriched HNItem data to database",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Persist the enriched HNItem to the database.

        Args:
            entity: The enriched HNItem to persist
            **kwargs: Additional processing parameters

        Returns:
            The persisted entity with storage metadata
        """
        try:
            self.logger.info(
                f"Persisting HNItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItem for type-safe operations
            hn_item = cast_entity(entity, HNItem)

            # Add storage timestamp
            hn_item.stored_at = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Mark as persisted
            hn_item.storage_status = "persisted"

            # Note: The actual persistence is handled by the Cyoda framework
            # when this processor returns. We just mark the entity as ready
            # for storage and add metadata.

            self.logger.info(f"HNItem {hn_item.technical_id} marked for persistence")

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error persisting HNItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark storage as failed
            if hasattr(entity, "storage_status"):
                entity.storage_status = "failed"
            raise
