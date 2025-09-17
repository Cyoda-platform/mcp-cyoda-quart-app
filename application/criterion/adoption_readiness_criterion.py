"""
AdoptionReadinessCriterion for Purrfect Pets API

Checks if a pet is ready for adoption completion.
"""

from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class AdoptionReadinessCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if a pet is ready for adoption completion.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AdoptionReadinessCriterion",
            description="Checks if a pet is ready for adoption completion",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the pet is ready for adoption completion.

        Args:
            entity: The Pet entity to check
            **kwargs: Additional criteria parameters (adoptionDetails)

        Returns:
            True if the pet is ready for adoption, False otherwise
        """
        try:
            self.logger.info(
                f"Checking adoption readiness for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get adoption details from kwargs
            adoption_details = kwargs.get("adoptionDetails", {})

            # Check if pet's current state is RESERVED
            if not pet.is_reserved():
                self.logger.info(
                    f"Pet {pet.technical_id} is not reserved (current state: {pet.state})"
                )
                return False

            # Check if adoption contract is signed
            contract_signed = adoption_details.get("contractSigned", False)
            if not contract_signed:
                self.logger.info(f"Pet {pet.technical_id} adoption contract not signed")
                return False

            # Check if adoption fee is received
            fee_received = adoption_details.get("feeReceived", False)
            if not fee_received:
                self.logger.info(f"Pet {pet.technical_id} adoption fee not received")
                return False

            # Check if pet is vaccinated
            if not pet.vaccinated:
                self.logger.info(f"Pet {pet.technical_id} is not vaccinated")
                return False

            self.logger.info(f"Pet {pet.technical_id} is ready for adoption")
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking adoption readiness for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
