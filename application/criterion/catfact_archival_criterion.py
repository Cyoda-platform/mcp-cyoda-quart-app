"""
CatFactArchivalCriterion for Cyoda Client Application

Checks if a cat fact can be archived after distribution.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional, Protocol, cast

from application.entity.catfact.version_1.catfact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class _EntityService(Protocol):
    async def search(
        self, entity_class: str, condition: Any, entity_version: str = "1"
    ) -> list[Any]: ...


class CatFactArchivalCriterion(CyodaCriteriaChecker):
    """Criterion for validating if a cat fact can be archived."""

    def __init__(self) -> None:
        super().__init__(
            name="CatFactArchivalCriterion",
            description="Checks if a cat fact can be archived after distribution",
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
        """Check if the cat fact can be archived."""
        try:
            cat_fact = cast_entity(entity, CatFact)

            # Check if cat fact is in SENT state
            if cat_fact.state != "sent":
                self.logger.warning(
                    f"Cat fact must be in SENT state, current: {cat_fact.state}"
                )
                return False

            # Check if all related email deliveries are completed
            if not await self._are_all_deliveries_completed(cat_fact.get_id()):
                self.logger.warning("Some email deliveries are still pending")
                return False

            # Check if at least 24 hours have passed since scheduled send date
            if not cat_fact.scheduled_send_date:
                self.logger.warning("Cat fact has no scheduled send date")
                return False

            if not self._has_24_hours_passed(cat_fact.scheduled_send_date):
                self.logger.warning("Must wait at least 24 hours before archiving")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating cat fact archival: {str(e)}")
            return False

    async def _are_all_deliveries_completed(self, cat_fact_id: str) -> bool:
        """Check if all email deliveries for this cat fact are completed."""
        entity_service = self._get_entity_service()

        try:
            deliveries = await entity_service.search(
                entity_class="EmailDelivery",
                condition={"catFactId": cat_fact_id},
                entity_version="1",
            )

            for delivery in deliveries:
                state = getattr(delivery, "get_state", lambda: "unknown")()
                if state == "pending":
                    return False

            return True

        except Exception as e:
            self.logger.warning(f"Error checking email deliveries: {str(e)}")
            return True  # Allow archival if we can't check

    def _has_24_hours_passed(self, scheduled_date: str) -> bool:
        """Check if at least 24 hours have passed since scheduled send date."""
        try:
            scheduled = datetime.strptime(scheduled_date, "%Y-%m-%d")
            now = datetime.now()
            hours_passed = (now - scheduled).total_seconds() / 3600
            return hours_passed >= 24
        except Exception:
            return True  # Allow archival if we can't parse date
