"""
CompleteSaleProcessor for Cyoda Client Application

Handles the completion of Pet sales when they are sold.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class CompleteSaleProcessor(CyodaProcessor):
    """
    Processor for completing Pet sales when they are marked as sold.
    Sets sold date and updates timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CompleteSaleProcessor",
            description="Completes Pet sales by setting sold date and timestamp",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Complete the sale of the Pet entity according to functional requirements.

        Args:
            entity: The Pet entity to mark as sold
            **kwargs: Additional processing parameters

        Returns:
            The sold pet with sold date set
        """
        try:
            self.logger.info(
                f"Completing sale for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Set sold date and update timestamp
            pet.set_sold_date()

            self.logger.info(
                f"Pet {pet.technical_id} sale completed successfully"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error completing sale for pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
