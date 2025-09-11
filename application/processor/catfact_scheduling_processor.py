"""
CatFactSchedulingProcessor for Cyoda Client Application

Schedules cat fact for weekly distribution.
Calculates next send date and updates the entity.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, cast

from application.entity.catfact.version_1.catfact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CatFactSchedulingProcessor(CyodaProcessor):
    """
    Processor for scheduling cat facts for weekly distribution.
    Calculates next Monday as send date and updates the entity.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactSchedulingProcessor",
            description="Schedules cat fact for weekly distribution",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process cat fact scheduling according to functional requirements.

        Args:
            entity: The CatFact entity to schedule (must be in retrieved state)
            **kwargs: Additional processing parameters

        Returns:
            The CatFact entity with scheduled send date
        """
        try:
            self.logger.info(
                f"Processing cat fact scheduling {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Validate cat fact exists and is in retrieved state
            if cat_fact.state != "retrieved":
                raise ValueError(
                    f"Cat fact must be in retrieved state, current state: {cat_fact.state}"
                )

            if not cat_fact.fact_text or len(cat_fact.fact_text.strip()) == 0:
                raise ValueError("Cat fact text cannot be empty")

            # Calculate next send date (next Monday)
            next_monday = self._find_next_monday()

            # Schedule the cat fact for the calculated date
            cat_fact.schedule_for_date(next_monday)

            self.logger.info(
                f"Cat fact scheduled for {next_monday}: {cat_fact.fact_text[:50]}..."
            )

            return cat_fact

        except Exception as e:
            self.logger.error(
                f"Error processing cat fact scheduling {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _find_next_monday(self) -> str:
        """
        Find the next Monday from current date.

        Returns:
            Next Monday date in YYYY-MM-DD format
        """
        today = datetime.now().date()

        # Calculate days until next Monday
        # Monday is weekday 0, so we need to find the next occurrence
        days_ahead = 0 - today.weekday()  # 0 = Monday

        if days_ahead <= 0:  # Target day already happened this week or is today
            days_ahead += 7

        next_monday = today + timedelta(days=days_ahead)

        return next_monday.strftime("%Y-%m-%d")
