"""
CatFact Send Time Criterion for checking if it's time to send the scheduled cat fact.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.catfact.version_1.catfact import CatFact
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class CatFactSendTimeCriterion(CyodaCriteriaChecker):
    """Criteria checker to determine if it's time to send the scheduled cat fact."""

    def __init__(self, name: str = "CatFactSendTimeCriterion", description: str = ""):
        super().__init__(
            name=name,
            description=description
            or "Checks if it's time to send the scheduled cat fact",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if it's time to send the cat fact."""
        try:
            if not isinstance(entity, CatFact):
                return False

            # Check if scheduled send date is set
            if not entity.scheduledSendDate:
                return False

            # Get current time
            current_time = datetime.now(timezone.utc)

            # Parse scheduled send date
            scheduled_time = entity.scheduledSendDate
            if isinstance(scheduled_time, str):
                try:
                    scheduled_time = datetime.fromisoformat(
                        scheduled_time.replace("Z", "+00:00")
                    )
                except ValueError:
                    logger.error(f"Invalid scheduledSendDate format: {scheduled_time}")
                    return False

            # Check if current time is at or after scheduled time
            return current_time >= scheduled_time

        except Exception as e:
            logger.exception(
                f"Failed to check send time criteria for cat fact {entity.entity_id}"
            )
            raise CriteriaError(
                self.name, f"Failed to check send time criteria: {str(e)}", e
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, CatFact)
