"""
StoreActivationProcessor for Purrfect Pets API

Activates a new store and makes it operational.
"""

import logging
from typing import Any

from application.entity.store.version_1.store import Store
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class StoreActivationProcessor(CyodaProcessor):
    """
    Processor for Store activation that activates a new store and makes it operational.
    """

    def __init__(self) -> None:
        super().__init__(
            name="StoreActivationProcessor",
            description="Activates a new store and makes it operational",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Store activation according to functional requirements.

        Args:
            entity: The Store entity to process (must be in initial state)
            **kwargs: Additional processing parameters

        Returns:
            The processed store entity in active state
        """
        try:
            self.logger.info(
                f"Processing Store activation for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Store for type-safe operations
            store = cast_entity(entity, Store)

            # Validate store data (name, address, contact info required)
            self._validate_store_data(store)

            # Validate opening hours format (basic validation)
            self._validate_opening_hours(store.opening_hours)

            # Set current pet count to 0 (should already be set by default)
            if store.current_pet_count is None:
                store.current_pet_count = 0

            # Validate capacity is positive (already done in Store model validation)
            if store.capacity <= 0:
                raise ValueError("Store capacity must be positive")

            # Log store activation
            self.logger.info(
                f"Store {store.technical_id} ({store.name}) activated successfully"
            )

            return store

        except Exception as e:
            self.logger.error(
                f"Error processing store activation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_store_data(self, store: Store) -> None:
        """
        Validate store data according to functional requirements.

        Args:
            store: The Store entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Name, address, contact info are required (validated by Pydantic model)
        if not store.name or len(store.name.strip()) == 0:
            raise ValueError("Store name is required")

        if not store.address or len(store.address.strip()) == 0:
            raise ValueError("Store address is required")

        if not store.phone or len(store.phone.strip()) == 0:
            raise ValueError("Store phone is required")

        if not store.email or len(store.email.strip()) == 0:
            raise ValueError("Store email is required")

        if not store.manager_name or len(store.manager_name.strip()) == 0:
            raise ValueError("Store manager name is required")

        self.logger.debug(f"Store data validation passed for {store.name}")

    def _validate_opening_hours(self, opening_hours: str) -> None:
        """
        Validate opening hours format.

        Args:
            opening_hours: The opening hours string to validate

        Raises:
            ValueError: If validation fails
        """
        if not opening_hours or len(opening_hours.strip()) == 0:
            raise ValueError("Store opening hours are required")

        # Basic validation - just check it's not empty and reasonable length
        if len(opening_hours.strip()) > 200:
            raise ValueError("Opening hours description is too long")

        self.logger.debug(f"Opening hours validation passed: {opening_hours}")
