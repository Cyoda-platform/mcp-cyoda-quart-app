"""
ResetItemProcessor for Cyoda Client Application

Resets failed items for retry processing.
"""

import logging
from typing import Any

from application.entity.hnitem.version_1.hnitem import HnItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ResetItemProcessor(CyodaProcessor):
    """
    Processor for resetting failed items for retry processing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="reset_item_processor",
            description="Resets failed items for retry processing",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Reset the failed HN item for retry processing.

        Args:
            entity: The failed HnItem
            **kwargs: Additional processing parameters

        Returns:
            The reset entity ready for retry
        """
        try:
            self.logger.info(
                f"Resetting HnItem {getattr(entity, 'technical_id', '<unknown>')} for retry"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Reset the item for retry
            hn_item.reset_for_retry()

            self.logger.info(
                f"HnItem {hn_item.id} reset for retry. Attempt #{hn_item.retry_count}"
            )

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error resetting HnItem {getattr(entity, 'technical_id', '<unknown>')} for retry: {str(e)}"
            )
            raise
