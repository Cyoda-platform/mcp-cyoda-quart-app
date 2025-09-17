"""
StoreReopeningProcessor for Purrfect Pets API

Reopens a temporarily closed store.
"""

import logging
from typing import Any

from application.entity.store.version_1.store import Store
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class StoreReopeningProcessor(CyodaProcessor):
    """
    Processor for Store reopening that reopens a temporarily closed store.
    """

    def __init__(self) -> None:
        super().__init__(
            name="StoreReopeningProcessor",
            description="Reopens a temporarily closed store",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Store reopening according to functional requirements.

        Args:
            entity: The Store entity to process (must be temporarily closed)
            **kwargs: Additional processing parameters (reopening notes)

        Returns:
            The processed store entity in active state
        """
        try:
            self.logger.info(
                f"Processing Store reopening for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Store for type-safe operations
            store = cast_entity(entity, Store)

            # Get reopening information from kwargs
            reopening_notes = kwargs.get("reopeningNotes") or kwargs.get(
                "reopening_notes"
            )

            # Validate store is temporarily closed
            if not store.is_temporarily_closed():
                raise ValueError("Store must be temporarily closed to reopen")

            # Update closure record with actual reopening date
            # In a real system, you would update the StoreClosure entity
            # For this implementation, we log the reopening information

            reopening_info = f"Store reopened"
            if reopening_notes:
                reopening_info += f": {reopening_notes}"

            # Notify relevant stakeholders (in a real system)
            # This would involve sending notifications to staff, customers, etc.
            self.logger.info(
                f"Would notify stakeholders of store {store.technical_id} reopening"
            )

            # Log store reopening
            self.logger.info(
                f"Store {store.technical_id} ({store.name}) reopened. {reopening_info}"
            )

            return store

        except Exception as e:
            self.logger.error(
                f"Error processing store reopening {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
