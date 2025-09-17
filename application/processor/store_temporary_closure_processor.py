"""
StoreTemporaryClosureProcessor for Purrfect Pets API

Temporarily closes a store.
"""

import logging
from typing import Any

from application.entity.store.version_1.store import Store
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class StoreTemporaryClosureProcessor(CyodaProcessor):
    """
    Processor for Store temporary closure that temporarily closes a store.
    """

    def __init__(self) -> None:
        super().__init__(
            name="StoreTemporaryClosureProcessor",
            description="Temporarily closes a store",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Store temporary closure according to functional requirements.

        Args:
            entity: The Store entity to process (must be active)
            **kwargs: Additional processing parameters (closure reason, expected reopening date)

        Returns:
            The processed store entity in temporarily_closed state
        """
        try:
            self.logger.info(
                f"Processing Store temporary closure for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Store for type-safe operations
            store = cast_entity(entity, Store)

            # Get closure information from kwargs
            closure_reason = kwargs.get("closureReason") or kwargs.get("closure_reason")
            expected_reopening_date = kwargs.get("expectedReopeningDate") or kwargs.get(
                "expected_reopening_date"
            )

            # Validate store is currently active
            if not store.is_active():
                raise ValueError("Store must be active to temporarily close")

            # Validate closure reason is provided
            if not closure_reason:
                raise ValueError("Closure reason is required for temporary closure")

            # Create closure record with reason and expected reopening
            # In a real system, you might create a separate StoreClosure entity
            # For this implementation, we log the closure information

            closure_info = f"Temporarily closed: {closure_reason}"
            if expected_reopening_date:
                closure_info += f" (Expected reopening: {expected_reopening_date})"

            # Notify customers with pending applications (in a real system)
            # This would involve finding all pending adoption applications for this store
            # and notifying the customers
            self.logger.info(
                f"Would notify customers with pending applications for store {store.technical_id}"
            )

            # Log temporary closure
            self.logger.info(
                f"Store {store.technical_id} ({store.name}) temporarily closed. {closure_info}"
            )

            return store

        except Exception as e:
            self.logger.error(
                f"Error processing store temporary closure {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
