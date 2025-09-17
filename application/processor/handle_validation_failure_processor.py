"""
HandleValidationFailureProcessor for Cyoda Client Application

Handles validation failures and prepares items for retry or manual intervention.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.hnitem.version_1.hnitem import HnItem


class HandleValidationFailureProcessor(CyodaProcessor):
    """
    Processor for handling validation failures and preparing for retry or manual intervention.
    """

    def __init__(self) -> None:
        super().__init__(
            name="handle_validation_failure_processor",
            description="Handles validation failures and prepares items for retry or manual intervention",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Handle validation failure for the HN item.

        Args:
            entity: The HnItem with validation errors
            **kwargs: Additional processing parameters

        Returns:
            The entity with failure handling information
        """
        try:
            self.logger.info(
                f"Handling validation failure for HnItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Set failure information
            failure_details = "; ".join(hn_item.validation_errors or ["Unknown validation error"])
            hn_item.set_failure("validation_failed", failure_details)

            # Log validation failure
            self.logger.error(
                f"HN Item {hn_item.id} validation failed: {failure_details}"
            )

            self.logger.info(
                f"HnItem {hn_item.id} failure handling completed. Retry count: {hn_item.retry_count}"
            )

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error handling validation failure for HnItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
