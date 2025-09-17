"""
StorePermanentClosureProcessor for Purrfect Pets API

Permanently closes a store.
"""

import logging
from typing import Any

from application.entity.store.version_1.store import Store
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class StorePermanentClosureProcessor(CyodaProcessor):
    """
    Processor for Store permanent closure that permanently closes a store.
    """

    def __init__(self) -> None:
        super().__init__(
            name="StorePermanentClosureProcessor",
            description="Permanently closes a store",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Store permanent closure according to functional requirements.

        Args:
            entity: The Store entity to process (must be active or temporarily closed)
            **kwargs: Additional processing parameters (closure reason, closure date)

        Returns:
            The processed store entity in permanently_closed state
        """
        try:
            self.logger.info(
                f"Processing Store permanent closure for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Store for type-safe operations
            store = cast_entity(entity, Store)

            # Get closure information from kwargs
            closure_reason = kwargs.get("closureReason") or kwargs.get("closure_reason")
            closure_date = kwargs.get("closureDate") or kwargs.get("closure_date")

            # Validate store is currently active or temporarily closed
            if store.is_permanently_closed():
                raise ValueError("Store is already permanently closed")

            # Validate closure reason is provided
            if not closure_reason:
                raise ValueError("Closure reason is required for permanent closure")

            # Transfer all pets to other stores (in a real system)
            # This would involve finding all pets at this store and transferring them
            self.logger.info(
                f"Would transfer all pets from store {store.technical_id} to other stores"
            )

            # Cancel all pending adoption applications (in a real system)
            # This would involve finding all pending applications for this store and cancelling them
            self.logger.info(
                f"Would cancel all pending adoption applications for store {store.technical_id}"
            )

            # Create permanent closure record
            # In a real system, you might create a separate StoreClosure entity
            closure_info = f"Permanently closed: {closure_reason}"
            if closure_date:
                closure_info += f" (Closure date: {closure_date})"

            # Log permanent closure
            self.logger.info(
                f"Store {store.technical_id} ({store.name}) permanently closed. {closure_info}"
            )

            return store

        except Exception as e:
            self.logger.error(
                f"Error processing store permanent closure {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
