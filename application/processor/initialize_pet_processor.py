"""
InitializePetProcessor for Cyoda Client Application

Handles the initialization of Pet instances when they are first created.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class InitializePetProcessor(CyodaProcessor):
    """
    Processor for initializing Pet entities when they are first created.
    Sets availability date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="InitializePetProcessor",
            description="Initializes Pet instances with availability date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Initialize the Pet entity according to functional requirements.

        Args:
            entity: The Pet entity to initialize
            **kwargs: Additional processing parameters

        Returns:
            The initialized pet with availability date set
        """
        try:
            self.logger.info(
                f"Initializing Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Set availability date and update timestamp
            pet.set_availability_date()

            self.logger.info(
                f"Pet {pet.technical_id} initialized successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error initializing pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
