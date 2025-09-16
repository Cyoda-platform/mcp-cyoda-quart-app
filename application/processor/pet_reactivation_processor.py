"""
PetReactivationProcessor for Purrfect Pets Application

Reactivates an unavailable pet as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetReactivationProcessor(CyodaProcessor):
    """
    Processor for reactivating Pet entities from unavailable status.
    Validates pet health and condition before making available.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReactivationProcessor",
            description="Reactivate an unavailable pet"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for reactivation.

        Args:
            entity: The Pet entity to reactivate
            **kwargs: Additional processing parameters

        Returns:
            The reactivated Pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet reactivation for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet health information is current
            if pet.vaccinated is False:
                self.logger.warning(f"Pet {pet.technical_id} is not vaccinated - proceeding with reactivation")

            # Validate pet is still in good condition
            if pet.age is not None and pet.age > 240:  # 20 years
                self.logger.warning(f"Pet {pet.technical_id} is quite old ({pet.age} months) - proceeding with reactivation")

            # Update any changed information (this would typically come from kwargs)
            health_data = kwargs.get('health_data', {})
            if health_data:
                if 'vaccinated' in health_data:
                    pet.vaccinated = health_data['vaccinated']
                if 'weight' in health_data:
                    pet.weight = health_data['weight']
                if 'description' in health_data:
                    pet.description = health_data['description']

            # Set pet updated timestamp
            pet.update_timestamp()

            self.logger.info(f"Pet reactivation processed successfully for {pet.technical_id}")
            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet reactivation for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
