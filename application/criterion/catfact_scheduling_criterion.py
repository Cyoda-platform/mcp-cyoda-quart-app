"""
CatFactSchedulingCriterion for Cyoda Client Application

Checks if a cat fact can be scheduled for weekly distribution.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Protocol, cast

from application.entity.catfact.version_1.catfact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class _EntityService(Protocol):
    async def search(
        self, entity_class: str, condition: Any, entity_version: str = "1"
    ) -> list[Any]: ...


class CatFactSchedulingCriterion(CyodaCriteriaChecker):
    """
    Criterion for validating if a cat fact can be scheduled for weekly distribution.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactSchedulingCriterion",
            description="Checks if a cat fact can be scheduled for weekly distribution",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the cat fact meets all scheduling criteria.

        Args:
            entity: The CatFact entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if the cat fact can be scheduled, False otherwise
        """
        try:
            self.logger.info(
                f"Validating cat fact scheduling {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Check if cat fact is in RETRIEVED state
            if cat_fact.state != "retrieved":
                self.logger.warning(
                    f"Cat fact must be in RETRIEVED state, current: {cat_fact.state}"
                )
                return False

            # Check if cat fact text is not empty
            if not cat_fact.fact_text or len(cat_fact.fact_text.strip()) == 0:
                self.logger.warning("Cat fact text cannot be empty")
                return False

            # Check if cat fact text length is between 10 and 500 characters
            if cat_fact.fact_length < 10 or cat_fact.fact_length > 500:
                self.logger.warning(
                    f"Cat fact text must be between 10 and 500 characters, current: {cat_fact.fact_length}"
                )
                return False

            # Check if no other cat fact is scheduled for the same week
            next_monday = self._find_next_monday()
            if await self._is_fact_already_scheduled(next_monday):
                self.logger.warning(
                    f"Another cat fact is already scheduled for week starting {next_monday}"
                )
                return False

            self.logger.info(
                f"Cat fact {cat_fact.get_id()} passed all scheduling criteria"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error validating cat fact scheduling: {str(e)}")
            return False

    def _find_next_monday(self) -> str:
        """Find the next Monday from current date."""
        today = datetime.now().date()
        days_ahead = 0 - today.weekday()  # 0 = Monday

        if days_ahead <= 0:  # Target day already happened this week or is today
            days_ahead += 7

        next_monday = today + timedelta(days=days_ahead)
        return next_monday.strftime("%Y-%m-%d")

    async def _is_fact_already_scheduled(self, scheduled_date: str) -> bool:
        """Check if another cat fact is already scheduled for the given date."""
        entity_service = self._get_entity_service()

        try:
            existing_facts = await entity_service.search(
                entity_class="CatFact",
                condition={"scheduledSendDate": scheduled_date},
                entity_version="1",
            )

            return len(existing_facts) > 0

        except Exception as e:
            self.logger.warning(f"Error checking existing scheduled facts: {str(e)}")
            return False  # Allow scheduling if we can't check
