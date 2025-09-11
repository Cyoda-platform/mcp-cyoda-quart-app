"""
WeeklyScheduleFactAvailabilityCriterion for Cyoda Client Application

Checks if a cat fact is available for assignment to weekly schedule.
"""

import logging
from typing import Any, Optional, Protocol, cast

import httpx

from application.entity.weeklyschedule.version_1.weeklyschedule import WeeklySchedule
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class _EntityService(Protocol):
    async def search(
        self, entity_class: str, condition: Any, entity_version: str = "1"
    ) -> list[Any]: ...


class WeeklyScheduleFactAvailabilityCriterion(CyodaCriteriaChecker):
    """Criterion for checking if a cat fact is available for weekly schedule assignment."""

    def __init__(self) -> None:
        super().__init__(
            name="WeeklyScheduleFactAvailabilityCriterion",
            description="Checks if a cat fact is available for assignment to weekly schedule",
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
        """Check if a cat fact is available for assignment."""
        try:
            weekly_schedule = cast_entity(entity, WeeklySchedule)

            # Check if weekly schedule is in CREATED state
            if weekly_schedule.state != "created":
                self.logger.warning(
                    f"Weekly schedule must be in CREATED state, current: {weekly_schedule.state}"
                )
                return False

            # Check if there's a scheduled cat fact available
            if await self._has_scheduled_cat_fact(weekly_schedule.scheduled_send_date):
                self.logger.info("Scheduled cat fact available for assignment")
                return True

            # Check if we can retrieve a new cat fact from API
            if await self._can_retrieve_new_cat_fact():
                self.logger.info("Can retrieve new cat fact from API")
                return True

            self.logger.warning("No cat fact available and API is not accessible")
            return False

        except Exception as e:
            self.logger.error(f"Error checking cat fact availability: {str(e)}")
            return False

    async def _has_scheduled_cat_fact(self, scheduled_date: str) -> bool:
        """Check if there's a scheduled cat fact for the given date."""
        entity_service = self._get_entity_service()

        try:
            scheduled_facts = await entity_service.search(
                entity_class="CatFact",
                condition={"scheduledSendDate": scheduled_date, "state": "scheduled"},
                entity_version="1",
            )

            return len(scheduled_facts) > 0

        except Exception as e:
            self.logger.warning(f"Error checking scheduled cat facts: {str(e)}")
            return False

    async def _can_retrieve_new_cat_fact(self) -> bool:
        """Check if we can retrieve a new cat fact from the API."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://catfact.ninja/fact")
                response.raise_for_status()

                fact_data = response.json()
                if isinstance(fact_data, dict) and "fact" in fact_data:
                    return True

                return False

        except Exception as e:
            self.logger.warning(f"Cat Fact API is not available: {str(e)}")
            return False
