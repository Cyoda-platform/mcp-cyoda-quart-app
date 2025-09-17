"""
HandleStorageFailureProcessor for Cyoda Client Application

Handles storage failures and prepares items for retry.
"""

import logging
from typing import Any

from application.entity.hnitem.version_1.hnitem import HnItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class HandleStorageFailureProcessor(CyodaProcessor):
    """
    Processor for handling storage failures and preparing for retry.
    """

    def __init__(self) -> None:
        super().__init__(
            name="handle_storage_failure_processor",
            description="Handles storage failures and prepares items for retry",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Handle storage failure for the HN item.

        Args:
            entity: The HnItem with storage failure
            **kwargs: Additional processing parameters

        Returns:
            The entity with failure handling information
        """
        try:
            self.logger.info(
                f"Handling storage failure for HnItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Set failure information
            failure_details = hn_item.storage_error or "Unknown storage error"
            hn_item.set_failure("storage_failed", failure_details)

            # Log storage failure
            self.logger.error(f"HN Item {hn_item.id} storage failed: {failure_details}")

            self.logger.info(
                f"HnItem {hn_item.id} storage failure handling completed. Retry count: {hn_item.retry_count}"
            )

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error handling storage failure for HnItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
