"""
EntityExistsCriterion for Purrfect Pets API

Generic criterion to check if referenced entity exists according to criteria.md specification.
"""

from typing import Any, Dict, Optional, Protocol, cast

from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class _EntityService(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Dict[str, Any]]: ...


class EntityExistsCriterion(CyodaCriteriaChecker):
    """
    Generic criterion to check if referenced entity exists.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EntityExistsCriterion",
            description="Generic criterion to check if referenced entity exists",
        )
        self.entity_service: Optional[_EntityService] = None

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if referenced entity exists.

        Args:
            entity: The CyodaEntity (not used in this generic check)
            **kwargs: Additional criteria parameters including entity_id and entity_type

        Returns:
            True if entity exists, False otherwise
        """
        try:
            entity_id = kwargs.get("entity_id")
            entity_type = kwargs.get("entity_type")

            self.logger.info(f"Checking existence of {entity_type} with ID {entity_id}")

            # Check if entity ID is null
            if not entity_id:
                self.logger.warning("Entity ID is null")
                return False

            # Find entity by ID and type
            entity_service = self._get_entity_service()
            found_entity = await entity_service.get_by_id(
                entity_id=str(entity_id), entity_class=entity_type, entity_version="1"
            )

            # Check if entity is null
            if not found_entity:
                self.logger.warning(f"{entity_type} with ID {entity_id} not found")
                return False

            self.logger.info(f"{entity_type} with ID {entity_id} exists")
            return True

        except Exception as e:
            self.logger.error(f"Error checking entity existence: {str(e)}")
            return False
