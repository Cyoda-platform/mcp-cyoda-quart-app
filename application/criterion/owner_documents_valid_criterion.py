"""
OwnerDocumentsValidCriterion for Purrfect Pets Application

Validates that an Owner has provided valid verification documents
before they can proceed to the verified stage.
"""

from typing import Any

from application.entity.owner.version_1.owner import Owner
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class OwnerDocumentsValidCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Owner that checks if verification documents
    have been provided and are valid.
    """

    def __init__(self) -> None:
        super().__init__(
            name="OwnerDocumentsValidCriterion",
            description="Check if owner has provided valid verification documents",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the owner has provided valid verification documents.

        Args:
            entity: The CyodaEntity to validate (expected to be Owner)
            **kwargs: Additional criteria parameters

        Returns:
            True if the owner has valid documents, False otherwise
        """
        try:
            self.logger.info(
                f"Checking documents for owner {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Owner for type-safe operations
            owner = cast_entity(entity, Owner)

            # Check if verification documents are provided
            if not owner.has_verification_documents():
                self.logger.warning(
                    f"Owner {owner.technical_id} has not provided verification documents"
                )
                return False

            # Additional validation of document format/content could go here
            # For now, we just check that documents field is not empty
            documents = owner.verification_documents
            if documents and len(documents.strip()) > 0:
                self.logger.info(
                    f"Owner {owner.technical_id} has valid verification documents"
                )
                return True
            else:
                self.logger.warning(
                    f"Owner {owner.technical_id} has empty verification documents"
                )
                return False

        except Exception as e:
            self.logger.error(
                f"Error checking documents for owner {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
