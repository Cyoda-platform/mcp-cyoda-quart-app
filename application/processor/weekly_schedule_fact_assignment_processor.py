"""
WeeklyScheduleFactAssignmentProcessor for Cyoda Client Application

Assigns cat fact to weekly schedule.
"""

import logging
from typing import Any, Optional, Protocol, cast

from application.entity.weeklyschedule.version_1.weeklyschedule import WeeklySchedule
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _EntityService(Protocol):
    async def search(
        self, entity_class: str, condition: Any, entity_version: str = "1"
    ) -> list[Any]: ...

    async def save(
        self, *, entity: dict[str, Any], entity_class: str, entity_version: str
    ) -> Any: ...


class WeeklyScheduleFactAssignmentProcessor(CyodaProcessor):
    """Processor for assigning cat facts to weekly schedules."""

    def __init__(self) -> None:
        super().__init__(
            name="WeeklyScheduleFactAssignmentProcessor",
            description="Assigns cat fact to weekly schedule",
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

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process cat fact assignment to weekly schedule."""
        try:
            weekly_schedule = cast_entity(entity, WeeklySchedule)

            if weekly_schedule.state != "created":
                raise ValueError(
                    f"Weekly schedule must be in created state, current: {weekly_schedule.state}"
                )

            # Find available cat fact for this week
            available_cat_fact = await self._find_available_cat_fact(
                weekly_schedule.scheduled_send_date
            )

            if not available_cat_fact:
                # Trigger cat fact retrieval
                available_cat_fact = await self._retrieve_new_cat_fact()

            # Assign cat fact to schedule
            weekly_schedule.assign_cat_fact(available_cat_fact)

            self.logger.info(
                f"Cat fact {available_cat_fact} assigned to weekly schedule"
            )
            return weekly_schedule

        except Exception as e:
            self.logger.error(f"Error assigning cat fact to weekly schedule: {str(e)}")
            raise

    async def _find_available_cat_fact(self, scheduled_date: str) -> Optional[str]:
        """Find available cat fact for the scheduled date."""
        entity_service = self._get_entity_service()

        try:
            cat_facts = await entity_service.search(
                entity_class="CatFact",
                condition={"scheduledSendDate": scheduled_date, "state": "scheduled"},
                entity_version="1",
            )

            if cat_facts:
                return (
                    cat_facts[0].get_id() if hasattr(cat_facts[0], "get_id") else None
                )

            return None

        except Exception as e:
            self.logger.warning(f"Error finding available cat fact: {str(e)}")
            return None

    async def _retrieve_new_cat_fact(self) -> str:
        """Retrieve new cat fact from API."""
        entity_service = self._get_entity_service()

        try:
            # Create new cat fact entity for retrieval
            cat_fact_data = {
                "factText": "",  # Will be populated by retrieval processor
                "factLength": 0,
            }

            response = await entity_service.save(
                entity=cat_fact_data, entity_class="CatFact", entity_version="1"
            )

            cat_fact_id = (
                response.metadata.id if hasattr(response, "metadata") else None
            )

            if not cat_fact_id:
                raise ValueError("Failed to create cat fact for retrieval")

            self.logger.info(f"New cat fact created for retrieval: {cat_fact_id}")
            return cat_fact_id

        except Exception as e:
            self.logger.error(f"Error retrieving new cat fact: {str(e)}")
            raise
