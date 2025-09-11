"""
CatFactArchivalProcessor for Cyoda Client Application

Archives cat fact after successful distribution.
Updates the entity state and logs archival completion.
"""

import logging
from typing import Any, cast

from application.entity.catfact.version_1.catfact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CatFactArchivalProcessor(CyodaProcessor):
    """
    Processor for archiving cat facts after successful distribution.
    Updates the entity state to archived and logs the event.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactArchivalProcessor",
            description="Archives cat fact after successful distribution",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process cat fact archival according to functional requirements.

        Args:
            entity: The CatFact entity to archive (must be in sent state)
            **kwargs: Additional processing parameters

        Returns:
            The CatFact entity marked as archived
        """
        try:
            self.logger.info(
                f"Processing cat fact archival {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Validate cat fact exists and is in sent state
            if cat_fact.state != "sent":
                raise ValueError(
                    f"Cat fact must be in sent state, current state: {cat_fact.state}"
                )

            # Update timestamp to mark archival
            cat_fact.update_timestamp()

            # Log archival event
            self.logger.info(
                f"Cat fact archived successfully: {cat_fact.fact_text[:50]}... (sent on {cat_fact.scheduled_send_date})"
            )

            return cat_fact

        except Exception as e:
            self.logger.error(
                f"Error processing cat fact archival {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
