"""
OwnerVerifiedCriterion for Purrfect Pets Application

Validates that the adopting owner is verified before an adoption
application can be approved.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.adoption.version_1.adoption import Adoption
from services.services import get_entity_service


class OwnerVerifiedCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Adoption that checks if the adopting owner
    is verified and eligible to adopt pets.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OwnerVerifiedCriterion",
            description="Check if the adopting owner is verified for pet adoption",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the adopting owner is verified.

        Args:
            entity: The CyodaEntity to validate (expected to be Adoption)
            **kwargs: Additional criteria parameters

        Returns:
            True if the owner is verified, False otherwise
        """
        try:
            self.logger.info(
                f"Checking owner verification for adoption {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Get the owner entity to check verification status
            owner_verified = await self._check_owner_verification(adoption.owner_id)

            if owner_verified:
                self.logger.info(
                    f"Owner {adoption.owner_id} is verified for adoption {adoption.technical_id}"
                )
                return True
            else:
                self.logger.warning(
                    f"Owner {adoption.owner_id} is not verified for adoption {adoption.technical_id}"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Error checking owner verification for adoption {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _check_owner_verification(self, owner_id: str) -> bool:
        """
        Check if the owner is verified by retrieving their entity.

        Args:
            owner_id: The ID of the owner to check

        Returns:
            True if owner is verified or active, False otherwise
        """
        try:
            entity_service = get_entity_service()

            # Get the owner entity
            owner_response = await entity_service.get_by_id(
                entity_id=owner_id,
                entity_class="Owner",
                entity_version="1"
            )

            if owner_response and owner_response.data:
                owner_data = owner_response.data
                
                # Check owner state - should be "verified" or "active"
                owner_state = getattr(owner_data, 'state', None)
                
                if owner_state in ["verified", "active"]:
                    self.logger.info(f"Owner {owner_id} has valid state: {owner_state}")
                    return True
                else:
                    self.logger.warning(f"Owner {owner_id} has invalid state for adoption: {owner_state}")
                    return False
            else:
                self.logger.warning(f"Owner {owner_id} not found")
                return False

        except Exception as e:
            self.logger.error(f"Error retrieving owner {owner_id}: {str(e)}")
            return False
